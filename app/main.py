from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import engine, Base
from .routers import auth, lineas, import_export, users
from .routers import api as api_router

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de Fibras", version="1.0.0")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(auth.router)
app.include_router(lineas.router)
app.include_router(import_export.router)
app.include_router(users.router)
app.include_router(api_router.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
