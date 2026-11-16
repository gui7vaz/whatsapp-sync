#!/bin/zsh
# Double-click opens WhatsApp Sync from Terminal (Terminal needs Full Disk Access).
cd "$(dirname "$0")"
exec /usr/bin/python3 -I whatsapp_export.py
