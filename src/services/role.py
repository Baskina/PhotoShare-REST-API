from functools import wraps
from fastapi import HTTPException, Depends, status
from typing import List
from src.entity.models import User
from src.services.auth import auth_service


def roles_required(allowed_roles: List[str]):
    """
    Decorator that checks if the current user has the allowed role

    Args:
        allowed_roles (List[str]): List of allowed roles

    Raises:
        HTTPException: If the current user does not have the allowed role
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(auth_service.get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator