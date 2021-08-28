#!/usr/bin/env bash

function install_scripts() {
    if [[ ! -d $HOME/.config/gcu/scripts ]]; then
        mkdir -p $HOME/.config/gcu/scripts
    fi

    # Explicit copy so changes are copied in, if any were made.
    cp scripts/* $HOME/.config/gcu/scripts/.

    # Some of the scripts have special Python packages that need to be installed.
    python3 -m pip install -r requirements.txt
}

function install_manpages() {
    if [[ ! -d $HOME/.config/gcu/man ]]; then
        mkdir -p $HOME/.config/gcu/man/man1
    fi

    # Explicit copy so changes are copied in, if any were made.
    cp man/* $HOME/.config/gcu/man/man1/.
}

# User should explicitly request which things to install.
# The symlink option symlinks the scripts and manpages instead of just copying.
if [[ $# -lt 1 ]]; then
    echo "usage: $0 --[all, scripts, manpages, symlink]"
fi

scripts=false
manpages=false
symlink=false

for i in "$@"; do
    case $i in
        -s|--scripts)
            scripts=true
            ;;
        -m|--manpages)
            manpages=true
            ;;
        -l|--symlink)
            symlink=true
            ;;
        -a|--all)
            scripts=true
            manpages=true
            ;;
    esac
done

# Create the config directory if it doesn't exist.
if [[ ! -d $HOME/.config ]]; then
    mkdir $HOME/.config
fi

# If symlinking, then that's all we need to do.
if $symlink; then
    echo -n "Symlinking gitlab-canvas-utils... "
    rm -rf $HOME/.config/gcu
    ln -sf $PWD $HOME/.config/gcu
    echo "done."
    exit 0
fi

# Provide a template config if one doesn't exist already.
if [[ ! -f $HOME/.config/gcu/config.toml ]]; then
    echo "Configuration file missing, supplying template config."
    cp config.toml $HOME/.config/gcu/.
fi

# Install scripts if specified.
if $scripts; then
    echo -n "Installing scripts... "
    install_scripts
    echo "done."
    echo "To add the scripts to your \$PATH, run:"
    echo " $ export PATH=\$PATH:\$HOME/.config/gcu/scripts"
fi

# Install manpages if specified.
if $manpages; then
    echo -n "Installing manpages... "
    install_manpages
    echo "done."
    echo "To add the man pages to your \$MANPATH, run:"
    echo " $ export MANPATH=\$MANPATH::\$HOME/.config/gcu/share/man"
    echo "The double colon is not a typo."
fi
