from fastapi import APIRouter, Depends, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from ..database import get_db
from ..models import Linea, User
from ..schemas import LineaCreate, LineaUpdate
from ..dependencies import get_current_user, require_editor, require_viewer

router = APIRouter(tags=["lineas"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    page: int = Query(1, ge=1),
    search: str = Query("", alias="q"),
    proveedor: str = Query(""),
    tipo_conectividad: str = Query(""),
    tipo_ip: str = Query(""),
    velocidad: str = Query(""),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    per_page = 25
    query = db.query(Linea)

    # Aplicar filtros
    if search:
        query = query.filter(
            or_(
                Linea.numero_linea.ilike(f"%{search}%"),
                Linea.sede.ilike(f"%{search}%"),
                Linea.servicio_conectividad.ilike(f"%{search}%"),
                Linea.cliente.ilike(f"%{search}%"),
                Linea.direccion_ip.ilike(f"%{search}%")
            )
        )

    if proveedor:
        query = query.filter(Linea.proveedor == proveedor)

    if tipo_conectividad:
        query = query.filter(Linea.tipo_conectividad == tipo_conectividad)

    if tipo_ip:
        query = query.filter(Linea.tipo_ip == tipo_ip)

    if velocidad:
        query = query.filter(Linea.velocidad_conexion == velocidad)

    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    lineas = query.offset((page - 1) * per_page).limit(per_page).all()

    # Obtener valores únicos para filtros
    proveedores = db.query(Linea.proveedor).distinct().all()
    tipos_conectividad = db.query(Linea.tipo_conectividad).distinct().all()
    tipos_ip = db.query(Linea.tipo_ip).distinct().all()
    velocidades = db.query(Linea.velocidad_conexion).distinct().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "lineas": lineas,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "search": search,
        "proveedor": proveedor,
        "tipo_conectividad": tipo_conectividad,
        "tipo_ip": tipo_ip,
        "velocidad": velocidad,
        "proveedores": [p[0] for p in proveedores if p[0]],
        "tipos_conectividad": [t[0] for t in tipos_conectividad if t[0]],
        "tipos_ip": [t[0] for t in tipos_ip if t[0]],
        "velocidades": [v[0] for v in velocidades if v[0]]
    })

@router.get("/lineas/search", response_class=HTMLResponse)
async def search_lineas(
    request: Request,
    q: str = Query(""),
    proveedor: str = Query(""),
    tipo_conectividad: str = Query(""),
    tipo_ip: str = Query(""),
    velocidad: str = Query(""),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return HTMLResponse("<p>No autorizado</p>", status_code=401)

    per_page = 25
    query = db.query(Linea)

    if q:
        query = query.filter(
            or_(
                Linea.numero_linea.ilike(f"%{q}%"),
                Linea.sede.ilike(f"%{q}%"),
                Linea.servicio_conectividad.ilike(f"%{q}%"),
                Linea.cliente.ilike(f"%{q}%"),
                Linea.direccion_ip.ilike(f"%{q}%")
            )
        )

    if proveedor:
        query = query.filter(Linea.proveedor == proveedor)

    if tipo_conectividad:
        query = query.filter(Linea.tipo_conectividad == tipo_conectividad)

    if tipo_ip:
        query = query.filter(Linea.tipo_ip == tipo_ip)

    if velocidad:
        query = query.filter(Linea.velocidad_conexion == velocidad)

    total = query.count()
    total_pages = (total + per_page - 1) // per_page
    lineas = query.offset((page - 1) * per_page).limit(per_page).all()

    return templates.TemplateResponse("partials/lineas_table.html", {
        "request": request,
        "user": user,
        "lineas": lineas,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "search": q,
        "proveedor": proveedor,
        "tipo_conectividad": tipo_conectividad,
        "tipo_ip": tipo_ip,
        "velocidad": velocidad
    })

@router.get("/lineas/new", response_class=HTMLResponse)
async def new_linea_form(
    request: Request,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse("linea_form.html", {
        "request": request,
        "user": user,
        "linea": None,
        "action": "crear"
    })

@router.post("/lineas")
async def create_linea(
    request: Request,
    numero_linea: str = Form(...),
    proveedor: str = Form("Movistar"),
    servicio_conectividad: str = Form(""),
    sede: str = Form(""),
    tipo_conectividad: str = Form(""),
    velocidad_conexion: str = Form(""),
    tipo_ip: str = Form(""),
    tipo_mantenimiento: str = Form(""),
    cliente: str = Form(""),
    direccion_ip: str = Form(""),
    notas: str = Form(""),
    user: User = Depends(require_editor),
    db: Session = Depends(get_db)
):
    existing = db.query(Linea).filter(Linea.numero_linea == numero_linea).first()
    if existing:
        return templates.TemplateResponse("linea_form.html", {
            "request": request,
            "user": user,
            "linea": None,
            "action": "crear",
            "error": "Ya existe una línea con ese número"
        })

    linea = Linea(
        numero_linea=numero_linea,
        proveedor=proveedor,
        servicio_conectividad=servicio_conectividad,
        sede=sede,
        tipo_conectividad=tipo_conectividad,
        velocidad_conexion=velocidad_conexion,
        tipo_ip=tipo_ip,
        tipo_mantenimiento=tipo_mantenimiento,
        cliente=cliente,
        direccion_ip=direccion_ip,
        notas=notas
    )
    db.add(linea)
    db.commit()
    return RedirectResponse(url=f"/lineas/{linea.id}", status_code=303)

@router.get("/lineas/{linea_id}", response_class=HTMLResponse)
async def view_linea(
    request: Request,
    linea_id: int,
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    linea = db.query(Linea).filter(Linea.id == linea_id).first()
    if not linea:
        raise HTTPException(status_code=404, detail="Línea no encontrada")

    return templates.TemplateResponse("linea_detail.html", {
        "request": request,
        "user": user,
        "linea": linea
    })

@router.get("/lineas/{linea_id}/edit", response_class=HTMLResponse)
async def edit_linea_form(
    request: Request,
    linea_id: int,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db)
):
    linea = db.query(Linea).filter(Linea.id == linea_id).first()
    if not linea:
        raise HTTPException(status_code=404, detail="Línea no encontrada")

    return templates.TemplateResponse("linea_form.html", {
        "request": request,
        "user": user,
        "linea": linea,
        "action": "editar"
    })

@router.post("/lineas/{linea_id}")
async def update_linea(
    request: Request,
    linea_id: int,
    numero_linea: str = Form(...),
    proveedor: str = Form("Movistar"),
    servicio_conectividad: str = Form(""),
    sede: str = Form(""),
    tipo_conectividad: str = Form(""),
    velocidad_conexion: str = Form(""),
    tipo_ip: str = Form(""),
    tipo_mantenimiento: str = Form(""),
    cliente: str = Form(""),
    direccion_ip: str = Form(""),
    notas: str = Form(""),
    user: User = Depends(require_editor),
    db: Session = Depends(get_db)
):
    linea = db.query(Linea).filter(Linea.id == linea_id).first()
    if not linea:
        raise HTTPException(status_code=404, detail="Línea no encontrada")

    # Verificar duplicado
    existing = db.query(Linea).filter(
        Linea.numero_linea == numero_linea,
        Linea.id != linea_id
    ).first()
    if existing:
        return templates.TemplateResponse("linea_form.html", {
            "request": request,
            "user": user,
            "linea": linea,
            "action": "editar",
            "error": "Ya existe otra línea con ese número"
        })

    linea.numero_linea = numero_linea
    linea.proveedor = proveedor
    linea.servicio_conectividad = servicio_conectividad
    linea.sede = sede
    linea.tipo_conectividad = tipo_conectividad
    linea.velocidad_conexion = velocidad_conexion
    linea.tipo_ip = tipo_ip
    linea.tipo_mantenimiento = tipo_mantenimiento
    linea.cliente = cliente
    linea.direccion_ip = direccion_ip
    linea.notas = notas
    db.commit()
    return RedirectResponse(url=f"/lineas/{linea_id}", status_code=303)

@router.post("/lineas/{linea_id}/delete")
async def delete_linea(
    linea_id: int,
    user: User = Depends(require_editor),
    db: Session = Depends(get_db)
):
    linea = db.query(Linea).filter(Linea.id == linea_id).first()
    if not linea:
        raise HTTPException(status_code=404, detail="Línea no encontrada")

    db.delete(linea)
    db.commit()
    return RedirectResponse(url="/", status_code=303)
