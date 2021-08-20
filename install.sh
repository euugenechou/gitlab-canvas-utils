#!/bin/bash

echo "Installing gitlab-canvas-utils scripts and man pages..."

if [[ ! -d $HOME/.config/gcu ]]; then
    echo -n " - gitlab-canvas-utils directory not found, creating... "
    mkdir -p $HOME/.config/gcu
    echo "done."
fi

if [[ ! -f $HOME/.config/gcu/config.json ]]; then
    echo -n " - config not found, supplying template config... "
    cp config.json $HOME/.config/gcu/.
    echo "done."
fi

if [[ ! -d $HOME/.config/gcu/scripts ]]; then
    echo -n " - script directory not found, creating and populating... "
    mkdir -p $HOME/.config/gcu/scripts
    echo "done."
fi

# Explicit copy so changes are copied in, if any were made.
cp scripts/* $HOME/.config/gcu/scripts/.

if [[ ! -d $HOME/.config/gcu/man ]]; then
    echo -n " - man page directory not found, creating and populating... "
    mkdir -p $HOME/.config/gcu/man/man1
    echo "done."
fi

# Explicit copy so changes are copied in, if any were made.
cp man/* $HOME/.config/gcu/man/man1/.

# Some of the scripts have special Python packages that need to be installed.
python3 -m pip install -r requirements.txt

echo "Installation complete."
echo "To add the scripts to your \$PATH, run:"
echo " $ export PATH=\$PATH:\$HOME/.config/gcu/scripts"
echo "To add the man pages to your \$MANPATH, run:"
echo " $ export MANPATH=\$MANPATH::\$HOME/.config/gcu/share/man"
echo "The double colon is not a typo."
echo "You may want to add these to your shell config."
