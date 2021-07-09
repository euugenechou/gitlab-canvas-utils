#!/bin/bash

echo "Installing gitlab-canvas-utils scripts and man pages..."

if [[ ! -d $HOME/.config/guc ]]; then
    echo -n " - gitlab-canvas-utils directory not found, creating... "
    mkdir -p $HOME/.config/guc
    echo "done."
fi

if [[ ! -f $HOME/.config/guc/config.json ]]; then
    echo -n " - config not found, supplying template config... "
    cp config.json $HOME/.config/guc/.
    echo "done."
fi

if [[ ! -d $HOME/.config/guc/scripts ]]; then
    echo -n " - script directory not found, creating and populating... "
    mkdir -p $HOME/.config/guc/scripts
    echo "done."
fi

# Explicit copy so changes are copied in, if any were made.
cp scripts/* $HOME/.config/guc/scripts/.

if [[ ! -d $HOME/.config/guc/man ]]; then
    echo -n " - man page directory not found, creating and populating... "
    mkdir -p $HOME/.config/guc/man/man1
    echo "done."
fi

# Explicit copy so changes are copied in, if any were made.
cp man/* $HOME/.config/guc/man/man1/.

echo "Installation complete."
echo "To add the scripts to your \$PATH, run:"
echo " $ export PATH=\$PATH:\$HOME/.config/guc/scripts"
echo "To add the man pages to your \$MANPATH, run:"
echo " $ export MANPATH=\$MANPATH:\$HOME/.config/guc/share/man"
echo "You may want to add these to your shell config."
