"""API REST con token Bearer para integraciones externas (ARIS, etc).
Separado del auth web por sesion: aqui no hay cookies, solo Bearer token."""
import os
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models import Linea

router = APIRouter(prefix="/api", tags=["api"])

# Token de servicio: lo configuramos en .env como FIBRAS_API_TOKEN
SERVICE_TOKEN = os.environ.get("FIBRAS_API_TOKEN", "")


def require_bearer(request: Request):
    """Comprueba header Authorization: Bearer <token>. 401 si falta o no coincide."""
    if not SERVICE_TOKEN:
        raise HTTPException(503, "FIBRAS_API_TOKEN no configurado en .env")
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Falta header Authorization Bearer")
    token = auth[7:].strip()
    if token != SERVICE_TOKEN:
        raise HTTPException(401, "Token invalido")
    return True


def _serialize_linea(l: Linea) -> dict:
    return {
        "id": l.id,
        "numero_linea": l.numero_linea or "",
        "cliente": l.cliente or "",
        "sede": l.sede or "",
        "direccion_ip": l.direccion_ip or "",
        "tipo_ip": l.tipo_ip or "",
        "proveedor": l.proveedor or "",
        "servicio_conectividad": l.servicio_conectividad or "",
        "tipo_conectividad": l.tipo_conectividad or "",
        "velocidad_conexion": l.velocidad_conexion or "",
        "tipo_mantenimiento": l.tipo_mantenimiento or "",
        "notas": l.notas or "",
    }


@router.get("/lineas/search", dependencies=[Depends(require_bearer)])
def api_lineas_search(
    q: str = Query("", description="Termino: cliente/numero/IP/sede/proveedor"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = (q or "").strip()
    if not q:
        return {"query": q, "count": 0, "results": []}
    like = f"%{q}%"
    rows = (
        db.query(Linea)
        .filter(or_(
            Linea.cliente.ilike(like),
            Linea.numero_linea.ilike(like),
            Linea.direccion_ip.ilike(like),
            Linea.sede.ilike(like),
            Linea.proveedor.ilike(like),
        ))
        .order_by(Linea.cliente.asc())
        .limit(limit)
        .all()
    )
    return {
        "query": q,
        "count": len(rows),
        "results": [_serialize_linea(r) for r in rows],
    }


@router.get("/lineas/{linea_id}", dependencies=[Depends(require_bearer)])
def api_lineas_get(linea_id: int, db: Session = Depends(get_db)):
    l = db.get(Linea, linea_id)
    if not l:
        raise HTTPException(404, "linea_not_found")
    return _serialize_linea(l)
