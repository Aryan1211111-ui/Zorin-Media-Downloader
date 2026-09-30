#!/bin/bash
# Native Zorin OS App Package Installer Script

echo "======================================================"
echo "    Zorin OS Media Downloader Native Installer       "
echo "======================================================"
echo ""

# Ensure we are inside the target folder space
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 1. Moving Application Assets to system bin space
echo "[1/3] Copying application code to your local bin space..."
mkdir -p "$HOME/.local/bin"
cp "$DIR/zorin-downloader.py" "$HOME/.local/bin/zorin-downloader"
chmod +x "$HOME/.local/bin/zorin-downloader"

# 2. Creating Custom Zorin Desktop UI Entry File Configuration
echo "[2/3] Registering Application into the Zorin OS Desktop Environment Start Menu..."
mkdir -p "$HOME/.local/share/applications"

cat << EOF > "$HOME/.local/share/applications/zorin-downloader.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Zorin Media Downloader
Comment=Download premium media streams, audio extracts, and vector images directly
Exec=$HOME/.local/bin/zorin-downloader
Icon=system-software-install
Terminal=false
Categories=Utility;Network;
OnlyShowIn=XFCE;GNOME;Zorin;
StartupNotify=true
EOF

chmod +x "$HOME/.local/share/applications/zorin-downloader.desktop"

# 3. Inform system shell index changes
echo "[3/3] Synchronizing Zorin applications application caches..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
fi

echo ""
echo "✨ Installation Success! ✨"
echo "You can now search for 'Zorin Media Downloader' directly inside your Zorin OS Start Menu!"
echo "======================================================"
