#!/bin/bash
# Instala la aplicación como servicio systemd

set -e

# Detectar usuario y directorio actual
APP_USER=$(whoami)
APP_DIR=$(pwd)

echo "=== Configurando servicio systemd ==="
echo "Usuario: $APP_USER"
echo "Directorio: $APP_DIR"

# Crear archivo de servicio
sudo tee /etc/systemd/system/fibras.service > /dev/null << EOF
[Unit]
Description=Fibras App - Gestión de Conectividad
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "=== Habilitando servicio ==="
sudo systemctl daemon-reload
sudo systemctl enable fibras
sudo systemctl start fibras

echo ""
echo "=== SERVICIO INSTALADO ==="
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status fibras    # Ver estado"
echo "  sudo systemctl restart fibras   # Reiniciar"
echo "  sudo systemctl stop fibras      # Detener"
echo "  sudo journalctl -u fibras -f    # Ver logs"
echo ""
echo "La aplicación está disponible en: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
