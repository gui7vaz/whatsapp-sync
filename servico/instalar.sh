#!/bin/zsh
# Installs (or reinstalls) the WhatsApp Sync background service.
# Remove:  servico/instalar.sh remove
# Rebuild the launcher: servico/instalar.sh rebuild (macOS will ask for Full Disk Access again)
set -e
cd "$(dirname "$0")/.."
PROJ="$PWD"
DATA="$HOME/Library/Application Support/WhatsApp Sync"
APP="$PROJ/WhatsApp Sync.app"
LABEL="com.whatsapp-sync"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
if [[ "$1" == "remove" || "$1" == "remover" ]]; then
  rm -f "$PLIST"
  echo "Service removed. (The app folder, your settings and the exported .md files stay.)"
  exit 0
fi

# the launcher is only built if missing: rebuilding changes its signature and
# macOS asks for Full Disk Access again
if [[ ! -x "$APP/Contents/MacOS/whatsapp-sync" || "$1" == "rebuild" || "$1" == "recompilar" ]]; then
  rm -rf "$APP"
  mkdir -p "$APP/Contents/MacOS"
  cc -O2 -o "$APP/Contents/MacOS/whatsapp-sync" servico/launcher.c
  cat > "$APP/Contents/Info.plist" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>WhatsApp Sync</string>
  <key>CFBundleIdentifier</key><string>$LABEL</string>
  <key>CFBundleExecutable</key><string>whatsapp-sync</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSUIElement</key><true/>
</dict></plist>
PL
  codesign --force --sign - "$APP"
fi

mkdir -p "$DATA/logs" "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>$APP/Contents/MacOS/whatsapp-sync</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>$DATA/logs/servico.log</string>
  <key>StandardErrorPath</key><string>$DATA/logs/servico.log</string>
</dict></plist>
PL
pkill -f "whatsapp_export.py" 2>/dev/null || true
sleep 1
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Service installed: it starts at login and syncs in the background."
echo "Next: System Settings > Privacy & Security > Full Disk Access > turn on \"WhatsApp Sync\"."
echo "Then open http://whatsapp-sync.localhost:8765"
