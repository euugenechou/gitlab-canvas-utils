#!/bin/bash

echo "Uninstalling gitlab-canvas-utils scripts and man pages..."

if [[ -d $HOME/.config/guc ]]; then
    echo -n "gitlab-canvas-utils directory found, removing... "
    rm -rf $HOME/.config/guc
    echo "done."
fi

echo "Uninstallation complete."
echo "You may want to revert your \$PATH and \$MANPATH."
