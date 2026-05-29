#!/usr/bin/env sh
set -eu

repo="YuxuanSun123/cli-model-switcher"
branch="main"
codex_home="${CODEX_HOME:-$HOME/.codex}"
install_dir="$codex_home/skills/cli-model-switcher"
shell_name="auto"
recipes="opencode-openrouter,local-ollama"
active="opencode-openrouter"
mode="wizard"
dry_run="0"
no_install="0"

usage() {
  cat <<'EOF'
Install CLI Model Switcher on Linux, macOS, or WSL.

Usage:
  sh install.sh [options]

Options:
  --dir DIR          Install directory. Defaults to $CODEX_HOME/skills/cli-model-switcher or ~/.codex/skills/cli-model-switcher.
  --repo OWNER/REPO  GitHub repository. Defaults to YuxuanSun123/cli-model-switcher.
  --branch NAME      Git branch to install. Defaults to main.
  --shell NAME       Shell helper target: auto, bash, zsh, or fish. Defaults to auto.
  --recipes LIST     Comma-separated setup wizard recipes. Defaults to opencode-openrouter,local-ollama.
  --active NAME      Active setup profile. Defaults to opencode-openrouter.
  --full             Use setup --full instead of setup --wizard --yes.
  --no-install       Initialize profiles without writing shell helper files.
  --dry-run          Print and validate the planned install without cloning or writing files.
  -h, --help         Show this help.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dir)
      install_dir="$2"
      shift 2
      ;;
    --repo)
      repo="$2"
      shift 2
      ;;
    --branch)
      branch="$2"
      shift 2
      ;;
    --shell)
      shell_name="$2"
      shift 2
      ;;
    --recipes)
      recipes="$2"
      shift 2
      ;;
    --active)
      active="$2"
      shift 2
      ;;
    --full)
      mode="full"
      shift
      ;;
    --no-install)
      no_install="1"
      shift
      ;;
    --dry-run)
      dry_run="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$shell_name" in
  auto|bash|zsh|fish) ;;
  *)
    echo "Unsupported --shell value: $shell_name" >&2
    exit 2
    ;;
esac

find_python() {
  if [ -n "${AI_CLI_SWITCHER_PYTHON:-}" ]; then
    printf '%s\n' "$AI_CLI_SWITCHER_PYTHON"
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi
  echo "Python 3 was not found. Install Python 3 or set AI_CLI_SWITCHER_PYTHON." >&2
  exit 1
}

python_bin="$(find_python)"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

run_setup() {
  root="$1"
  setup_dry_run="${2:-0}"
  helper="$root/scripts/cli_model_switcher.py"
  if [ ! -f "$helper" ]; then
    echo "Missing helper script: $helper" >&2
    exit 1
  fi

  set -- "$helper" setup
  if [ "$mode" = "full" ]; then
    set -- "$@" --full
  else
    set -- "$@" --wizard --yes --recipes "$recipes" --active "$active"
  fi
  set -- "$@" --shell "$shell_name"
  if [ "$no_install" = "1" ]; then
    set -- "$@" --no-install
  fi
  if [ "$setup_dry_run" = "1" ]; then
    set -- "$@" --dry-run
  fi
  "$python_bin" "$@"
}

clone_or_update() {
  if [ -d "$install_dir/.git" ]; then
    git -C "$install_dir" fetch origin "$branch"
    git -C "$install_dir" checkout "$branch"
    git -C "$install_dir" pull --ff-only origin "$branch"
    return
  fi

  if [ -f "$install_dir/scripts/cli_model_switcher.py" ]; then
    echo "Using existing installation at $install_dir"
    return
  fi

  if [ -e "$install_dir" ] && [ "$(find "$install_dir" -mindepth 1 -maxdepth 1 2>/dev/null | head -n 1)" ]; then
    echo "Install directory is not empty and is not a CLI Model Switcher checkout: $install_dir" >&2
    exit 1
  fi

  if command -v git >/dev/null 2>&1; then
    mkdir -p "$(dirname "$install_dir")"
    git clone --depth 1 --branch "$branch" "https://github.com/$repo.git" "$install_dir"
    return
  fi

  tmp_dir="$(mktemp -d)"
  archive="$tmp_dir/source.tar.gz"
  archive_url="https://github.com/$repo/archive/refs/heads/$branch.tar.gz"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$archive_url" -o "$archive"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$archive" "$archive_url"
  else
    echo "Need git, curl, or wget to download $repo." >&2
    exit 1
  fi
  mkdir -p "$install_dir"
  tar -xzf "$archive" -C "$install_dir" --strip-components=1
  rm -rf "$tmp_dir"
}

echo "CLI Model Switcher installer"
echo "Repository: $repo"
echo "Branch: $branch"
echo "Install directory: $install_dir"
echo "Shell: $shell_name"
echo "Python: $python_bin"

if [ "$dry_run" = "1" ]; then
  echo "Dry run: would clone/update and run setup."
  if [ -f "$script_dir/scripts/cli_model_switcher.py" ]; then
    run_setup "$script_dir" "1"
  else
    echo "Dry run skipped setup execution because the helper script is not next to install.sh."
  fi
  exit 0
fi

clone_or_update
run_setup "$install_dir"

cat <<EOF

Installed CLI Model Switcher.

Open a new terminal or reload the shell profile printed above, then run:
  ai-status
  ai-doctor --fix

In each project where you want agent-side switching, run:
  ai-agent install all
EOF
