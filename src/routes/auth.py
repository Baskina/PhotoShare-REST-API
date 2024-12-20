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
        body (UserValidationSchema): The user's signup information.
        bt (BackgroundTasks): The background tasks to be executed.
        request (Request): The incoming request.
        db (AsyncSession): The database session. Defaults to Depends(get_db).

    Returns:
        UserValidationSchemaResponse: The newly created user's information.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.hash = auth_service.get_password_hash(body.hash)
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
        body (OAuth2PasswordRequestForm): The user's login credentials.
        db (AsyncSession): The database session.

    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.

    Raises:
        HTTPException: If the email is invalid, the email is not confirmed, or the password is invalid.
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
        # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


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
        credentials (HTTPAuthorizationCredentials): The user's refresh token credentials.
        db (AsyncSession): The database session.

    Returns:
        dict: A dictionary containing the new access token, refresh token, and token type.

    Raises:
        HTTPException: If the refresh token is invalid or expired.
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
        token (str): The email confirmation token.
        db (AsyncSession): The database session.

    Returns:
        dict: A dictionary containing a confirmation message.

    Raises:
        HTTPException: If the user account is not found or if the email is already confirmed.
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
