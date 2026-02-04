from typing import Optional, List
from functools import wraps
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .auth import decode_token

def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = get_token_from_cookie(request)
    if not token:
        return None

    payload = decode_token(token)
    if not payload:
        return None

    username: str = payload.get("sub")
    if not username:
        return None

    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        return None

    return user

def require_auth(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/login"}
        )
    return user

def require_role(allowed_roles: List[str]):
    def role_checker(request: Request, db: Session = Depends(get_db)):
        user = get_current_user(request, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/login"}
            )
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción"
            )
        return user
    return role_checker

require_admin = require_role(["admin"])
require_editor = require_role(["admin", "editor"])
require_viewer = require_role(["admin", "editor", "viewer"])
