from fastapi import (
    APIRouter,
    Depends,
    status,
    Security,
    HTTPException,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
    HTTPBearer,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import (
    users as repository_users,
)
from src.schemas.users import (
    UserValidationSchemaResponse,
    UserValidationSchema,
    TokenSchema,
)
from src.services.auth import (
    auth_service,
)
from src.services.email import (
    send_email,
)
from fastapi.security import OAuth2PasswordBearer
from src.entity.models import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

get_refresh_token = HTTPBearer()

@router.post(
    "/signup",
    response_model=UserValidationSchemaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    body: UserValidationSchema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles user signup by validating the provided information, checking for existing accounts,
    hashing the password, creating a new user, and sending a confirmation email.

    Args:
        body (UserValidationSchema): The user registration data, including email, password, and other details.
        bt (BackgroundTasks): A FastAPI BackgroundTasks instance for performing asynchronous operations (e.g., sending emails).
        request (Request): The HTTP request to build the base URL for email sending.
        db (AsyncSession): The database session used to query the database.

    Returns:
        UserValidationSchemaResponse: The newly created user data including the user's ID, email, username, and role.

    Raises:
        HTTPException: If the user already exists (409 Conflict).
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    
    body.hash = auth_service.get_password_hash(body.password)
    
    # If this is the first user, they will be an administrator
    user_count = await repository_users.count_users(db)
    if user_count == 0:
        body.role = "admin"
    
    new_user = await repository_users.create_user(body, db)

    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user

@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Handles user login by validating the provided credentials, checking for account confirmation,
    verifying the password, generating access and refresh tokens, and updating the user's token in the database.

    Args:
        body (OAuth2PasswordRequestForm): The user's login credentials, including username (email) and password.
        db (AsyncSession): The database session used to query the database.

    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.

    Raises:
        HTTPException: If the email is invalid (401 Unauthorized), the email is not confirmed (401 Unauthorized), 
                        or the password is incorrect (401 Unauthorized).
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login")),
    db: AsyncSession = Depends(get_db)
):
    """
    Logic for logging out the user.
    
    In a JWT-based authentication system, there is typically no need to delete the token server-side.
    Once the token expires, it is automatically invalid. However, if you want to immediately revoke the token,
    you can add it to a blacklist for immediate invalidation.

    Args:
        token (str): The user's access token to invalidate.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the user has successfully logged out.

    Example:
        {
            "message": "Successfully logged out"
        }
    """
    return {"message": "Successfully logged out"}

@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Handles refresh token requests by validating the provided refresh token,
    checking for account confirmation, verifying the token, generating new access
    and refresh tokens, and updating the user's token in the database.

    Args:
        credentials (HTTPAuthorizationCredentials): The user's refresh token to authenticate.
        db (AsyncSession): The database session.

    Returns:
        dict: A dictionary containing the new access token, refresh token, and token type.

    Raises:
        HTTPException: If the refresh token is invalid or expired (401 Unauthorized).
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Handles email confirmation requests by validating the provided confirmation token,
    checking for existing user accounts, verifying the user's confirmation status,
    updating the user's confirmation status in the database, and returning a confirmation message.

    Args:
        token (str): The email confirmation token to verify.
        db (AsyncSession): The database session.

    Returns:
        dict: A confirmation message indicating whether the email was confirmed or if it was already confirmed.

    Raises:
        HTTPException: If the user account is not found (400 Bad Request) or if the email is already confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Decodes the access token and retrieves the associated user from the database.

    Args:
        token (str): The user's access token.
        db (AsyncSession): The database session.

    Returns:
        User: The user object corresponding to the decoded token.

    Raises:
        HTTPException: If the token is invalid or the user does not exist (401 Unauthorized).
    """
    email = await auth_service.decode_access_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def role_required(required_role: str):
    """
    Decorator to enforce role-based access control on routes. Checks if the user has the required role.

    Args:
        required_role (str): The required role to access the route.

    Returns:
        function: A decorator function that checks the user's role before calling the decorated function.

    Raises:
        HTTPException: If the user's role does not match the required role (403 Forbidden).
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            user: User = await get_current_user(*args, **kwargs)
            if user.role != required_role:
                raise HTTPException(
                    status_code=403, detail=f"Permission denied. Role {required_role} required."
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@router.get("/admin_dashboard")
async def admin_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Access to the admin dashboard is allowed only for users with the "admin" role.

    Args:
        current_user (User): The current authenticated user, obtained from the access token.

    Returns:
        dict: A message welcoming the user to the Admin Dashboard.

    Raises:
        HTTPException: If the current user does not have the "admin" role (403 Forbidden).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Welcome to the Admin Dashboard"}

@router.get("/moderator_dashboard")
@role_required("moderator")
async def moderator_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Access to the moderator dashboard is allowed only for users with the "moderator" role.

    Args:
        current_user (User): The current authenticated user, obtained from the access token.

    Returns:
        dict: A message welcoming the user to the Moderator Dashboard.

    Raises:
        HTTPException: If the current user does not have the "moderator" role (403 Forbidden).
    """
    return {"message": "Welcome to the Moderator Dashboard"}

@router.get("/user_dashboard")
async def user_dashboard(
    current_user: User = Depends(get_current_user)
):
    """
    Provides access to the user dashboard. Available to all authenticated users.

    Args:
        current_user (User): The current authenticated user, obtained from the access token.

    Returns:
        dict: A message welcoming the user to the User Dashboard.
    """
    return {"message": "Welcome to the User Dashboard"}