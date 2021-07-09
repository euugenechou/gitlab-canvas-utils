# gitlab-canvas-utils

A collection of scripts originally written for CSE 13S. Oversees everything from
GitLab course group creation, student repository creation, all the way to
cloning repos and adding users to a shared resources repository.

## Installation

To install these utilities, run:

```bash
$ ./install.sh
```

Similarly, to uninstall, run:

```bash
$ ./uninstall.sh
```

## Paths

To get (arguably) the full experience of these utilities, you should add the
installed scripts directory to your `$PATH` and the installed man page directory
to your `$MANPATH`.

To add the scripts directory:

```bash
$ export PATH=$PATH:$HOME/.config/guc/scripts
```

To add the man directory:

```bash
$ export MANPATH=$MANPATH:$HOME/.config/guc/man
```
