#!/usr/bin/env bash
# {{{ Config

set -euo pipefail
PRODUCT_LOCATION=".gits"
INSTALL_DIR="$HOME/$PRODUCT_LOCATION"
VENV_DIR="$INSTALL_DIR/.venv"
PRODUCT_NAME="gits"
BIN_DIR="$HOME/.local/bin"
BIN_LINK="$BIN_DIR/$PRODUCT_NAME"
CONFIG_FILE="$HOME/.config/$PRODUCT_NAME/repository_locations.yml"
REPO_URL="https://github.com/Traap/gits.git"

echo "📦 Installing $PRODUCT_NAME to $INSTALL_DIR"

# -------------------------------------------------------------------------- }}}
# {{{ Ensure ~/.local/bin exists and is on PATH (persist for future shells)

mkdir -p "$BIN_DIR"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "⚠️  Adding $BIN_DIR to PATH (persisting in ~/.bashrc)"
  echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$HOME/.bashrc"
  export PATH="$BIN_DIR:$PATH"
fi

# -------------------------------------------------------------------------- }}}
# {{{ Platform Detection
is_arch=false
is_deb=false
is_gitbash=false

if [[ -f /etc/arch-release ]]; then
  is_arch=true
elif command -v apt >/dev/null 2>&1; then
  is_deb=true
fi

# -------------------------------------------------------------------------- }}}
# {{{ Git Bash detection (Windows): OSTYPE=msys or MSYSTEM or
#     uname shows mingw/msys.

if [[ "${OSTYPE:-}" == msys ]] || [[ -n "${MSYSTEM:-}" ]] || uname -a 2>/dev/null | grep -qiE 'mingw|msys'; then
  is_gitbash=true
fi

# -------------------------------------------------------------------------- }}}
# {{{ Ensure Linux packages

ensure_linux_pkg() {
  local pkg="$1"
  if ! command -v "$pkg" >/dev/null 2>&1; then
    echo "🔧 Installing $pkg..."
    if $is_arch; then
      sudo pacman -Sy --noconfirm "$pkg"
    elif $is_deb; then
      sudo apt update && sudo apt install -y "$pkg"
    fi
  fi
}

# -------------------------------------------------------------------------- }}}
# {{{ Ensure vu

ensure_uv() {
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi

  echo "🚀 uv not found. Installing..."
  if $is_arch; then
    sudo pacman -Sy --noconfirm uv
    return 0
  fi

  if $is_deb; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # uv often lands in ~/.cargo/bin or ~/.local/bin
    for d in "$HOME/.cargo/bin" "$HOME/.local/bin"; do
      if [[ -d "$d" ]] && [[ ":$PATH:" != *":$d:"* ]]; then
        echo "⚙️  Adding $d to PATH (persisting in ~/.bashrc)"
        echo "export PATH=\"$d:\$PATH\"" >> "$HOME/.bashrc"
        export PATH="$d:$PATH"
      fi
    done
    return 0
  fi

  if $is_gitbash; then
    # Prefer winget if available; fall back to PowerShell installer
    if command -v winget.exe >/dev/null 2>&1; then
      echo "🔧 Installing uv via winget..."
      set +e
      winget.exe install --id Astral.uv --silent --accept-package-agreements --accept-source-agreements
      if ! command -v uv >/dev/null 2>&1; then
        winget.exe install uv --silent --accept-package-agreements --accept-source-agreements
      fi
      set -e
    fi
    if ! command -v uv >/dev/null 2>&1; then
      echo "🔧 Installing uv via PowerShell bootstrap..."
      powershell.exe -NoProfile -Command "Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force; iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex"
    fi
    # On Windows (uv), default is %USERPROFILE%\.local\bin
    win_local_bin="$HOME/.local/bin"
    if [[ -d "$win_local_bin" ]] && [[ ":$PATH:" != *":$win_local_bin:"* ]]; then
      echo "⚙️  Adding $win_local_bin to PATH (persisting in ~/.bashrc)"
      echo "export PATH=\"$win_local_bin:\$PATH\"" >> "$HOME/.bashrc"
      export PATH="$win_local_bin:$PATH"
    fi
    return 0
  fi

  echo "❌ Unsupported OS for automatic uv install. Please install uv manually and re-run."
  exit 1
}

# -------------------------------------------------------------------------- }}}
# {{{ Prereqs (Linux)

if ! $is_gitbash; then
  ensure_linux_pkg git
  ensure_linux_pkg curl
fi

# -------------------------------------------------------------------------- }}}
# {{{ Ensure uv

ensure_uv

# -------------------------------------------------------------------------- }}}
# {{{ Fetch Source

if [[ ! -d "$INSTALL_DIR" ]]; then
  echo "📥 Cloning $REPO_URL"
  git clone "$REPO_URL" "$INSTALL_DIR"
else
  echo "📥 Updating existing repository"
  git -C "$INSTALL_DIR" fetch --all --prune
  git -C "$INSTALL_DIR" pull --ff-only || true
fi

# -------------------------------------------------------------------------- }}}
# {{{ Move to installation directory.

cd "$INSTALL_DIR"

# -------------------------------------------------------------------------- }}}
# {{{ Virtual Env

echo "🐍 Creating virtual environment..."
rm -rf "$VENV_DIR"
uv venv "$VENV_DIR"

# -------------------------------------------------------------------------- }}}
# {{{ Pick platform-appropriate layout

ACTIVATE=""
GITS_ENTRY=""
if [[ -f "$VENV_DIR/bin/activate" ]]; then
  ACTIVATE="$VENV_DIR/bin/activate"
  GITS_ENTRY="$VENV_DIR/bin/$PRODUCT_NAME"
elif [[ -f "$VENV_DIR/Scripts/activate" ]]; then
  ACTIVATE="$VENV_DIR/Scripts/activate"
  if [[ -f "$VENV_DIR/Scripts/${PRODUCT_NAME}.exe" ]]; then
    GITS_ENTRY="$VENV_DIR/Scripts/${PRODUCT_NAME}.exe"
  else
    GITS_ENTRY="$VENV_DIR/Scripts/${PRODUCT_NAME}"
  fi
else
  echo "❌ Unable to find venv activation script."
  exit 1
fi

# -------------------------------------------------------------------------- }}}
# {{{ Activate

# shellcheck disable=SC1090
source "$ACTIVATE"

# -------------------------------------------------------------------------- }}}
# {{{ Installing gits

echo "🔧 Installing project (editable)..."
uv pip install -e .

# -------------------------------------------------------------------------- }}}
# {{{ CLI Hook

mkdir -p "$BIN_DIR"

if $is_gitbash; then
  # Avoid symlinks on Windows (admin/dev-mode needed). Use a tiny launcher.
  echo "🔗 Installing launcher: $BIN_LINK → $GITS_ENTRY"
  cat > "$BIN_LINK" <<EOF
#!/usr/bin/env bash
set -euo pipefail
exec "$GITS_ENTRY" "\$@"
EOF
  chmod +x "$BIN_LINK"
else
  if [[ -f "$GITS_ENTRY" ]]; then
    ln -sf "$GITS_ENTRY" "$BIN_LINK"
    echo "🔗 Symlinked: $BIN_LINK → $GITS_ENTRY"
  fi
fi

# -------------------------------------------------------------------------- }}}
# {{{ Default Config

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "📝 Installing default config → $CONFIG_FILE"
  mkdir -p "$(dirname "$CONFIG_FILE")"
  cp -v repository_locations.yml "$CONFIG_FILE" || true
fi
echo "✅ Done! You can now run: $PRODUCT_NAME"

# -------------------------------------------------------------------------- }}}
