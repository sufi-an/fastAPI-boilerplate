from sqlalchemy import select
from fastapi import Request, HTTPException, status, Depends

from functools import wraps
from typing import Callable, List, Type
from jose import JWTError
from app.core.security import verify_token
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole


class BasePermission:
    def has_permission(self, user: User) -> bool:
        raise NotImplementedError


class IsSuperAdmin(BasePermission):
    def has_permission(self, user: User) -> bool:
        return user.role == UserRole.SUPER_ADMIN


class IsAdmin(BasePermission):
    def has_permission(self, user: User) -> bool:
        return user.role == UserRole.ADMIN


class IsTeacher(BasePermission):
    def has_permission(self, user: User) -> bool:
        return user.role == UserRole.TEACHER


def permissions(required: List[Type[BasePermission]]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or Invalid Token",
                )

            token = auth_header.replace("Bearer ", "")
            try:
                payload = verify_token(token)
                user_id = int(payload.get("sub"))
            except (JWTError, ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e),
                    headers={"www-Authenticate": "Bearer"},
                )

            db = AsyncSessionLocal()
            try:
                stmt = select(User).where(User.id == user_id)
                result = await db.execute(stmt)
                user = result.scalar_one_or_none()
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                    )

                for perm in required:
                    if not perm().has_permission(user):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Permission Denied",
                        )

                return await func(request, *args, **kwargs)
            finally:
                db.close()

        return wrapper

    return decorator
