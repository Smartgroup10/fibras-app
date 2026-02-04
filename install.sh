#!/bin/bash
# Script de instalación para Ubuntu/Debian

set -e

echo "=== Instalando dependencias del sistema ==="
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

echo "=== Creando entorno virtual ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Instalando dependencias Python ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Configurando .env ==="
if [ ! -f .env ]; then
    cp .env.example .env
    # Generar clave secreta aleatoria
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/cambia-esta-clave-en-produccion/$SECRET/" .env
    echo "Archivo .env creado con clave secreta aleatoria"
fi

echo "=== Inicializando base de datos ==="
python migrate_and_load.py

echo ""
echo "=== INSTALACION COMPLETADA ==="
echo ""
echo "Para iniciar la aplicación manualmente:"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "Para instalar como servicio systemd:"
echo "  sudo ./install_service.sh"
echo ""
