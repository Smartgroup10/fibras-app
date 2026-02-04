from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..auth import get_password_hash
from ..dependencies import require_admin

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
async def list_users(
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "user": user,
        "users": users,
        "editing": None,
        "error": None
    })

@router.get("/new", response_class=HTMLResponse)
async def new_user_form(
    request: Request,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user": user,
        "edit_user": None,
        "action": "crear"
    })

@router.post("")
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("viewer"),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Verificar duplicados
    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return templates.TemplateResponse("user_form.html", {
            "request": request,
            "user": user,
            "edit_user": None,
            "action": "crear",
            "error": "Ya existe un usuario con ese nombre o email"
        })

    new_user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/users", status_code=303)

@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    user_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return templates.TemplateResponse("user_form.html", {
        "request": request,
        "user": user,
        "edit_user": edit_user,
        "action": "editar"
    })

@router.post("/{user_id}")
async def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(""),
    role: str = Form("viewer"),
    is_active: bool = Form(True),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    edit_user = db.query(User).filter(User.id == user_id).first()
    if not edit_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar duplicados
    existing = db.query(User).filter(
        ((User.username == username) | (User.email == email)),
        User.id != user_id
    ).first()
    if existing:
        return templates.TemplateResponse("user_form.html", {
            "request": request,
            "user": user,
            "edit_user": edit_user,
            "action": "editar",
            "error": "Ya existe otro usuario con ese nombre o email"
        })

    edit_user.username = username
    edit_user.email = email
    edit_user.role = role
    edit_user.is_active = is_active

    if password:
        edit_user.password_hash = get_password_hash(password)

    db.commit()
    return RedirectResponse(url="/users", status_code=303)

@router.post("/{user_id}/delete")
async def delete_user(
    user_id: int,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    if user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")

    delete_user = db.query(User).filter(User.id == user_id).first()
    if not delete_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(delete_user)
    db.commit()
    return RedirectResponse(url="/users", status_code=303)
