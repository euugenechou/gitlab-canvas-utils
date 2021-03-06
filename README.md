# gitlab-canvas-utils

A collection of scripts originally written for CSE 13S. Oversees everything from
GitLab course group creation, student repository creation, all the way to
cloning repos and adding users to a shared resources repository.

## Installation

To install the included scripts, run:

```bash
./install --all
```

To install the scripts and `man` pages for development, run:

```bash
./install --symlink
```

To uninstall the scripts, run:

```bash
$ ./uninstall.sh
```

## Utilities

There are currently 7 scripts/utilities:
1. `addtorepos` - adds students to a set of specified repositories as reporters
2. `checkout` - checks out cloned student repositories to commit IDs submitted
   for a specific assignment.
3. `clone` - clones student repositories.
4. `createrepos` - creates course GitLab course and student repos.
5. `pushfiles` - adds files to cloned student repositories, pushing the changes.
6. `rmfiles` - removes files from cloned student repositories, pushing the
   changes.
7. `roster` - scrapes Canvas for a CSV of the student roster.

Read the supplied `man` pages for more information on each of these utilities.

##### Creating GitLab course, student repos, and adding students to resources repository

```bash
$ roster | createrepos | addtoresources
```
##### Cloning all student repos and checking them out to submitted commit IDs

```bash
$ roster | clone | checkout --asgn=5
```

## Paths

To get (arguably) the full experience of these utilities, you should add the
installed scripts directory to your `$PATH` and the installed man page directory
to your `$MANPATH`.

To add the `scripts` directory:

```bash
$ export PATH=$PATH:$HOME/.config/gcu/scripts
```

To add the `man` directory (the double colon is intentional):

```bash
$ export MANPATH=::$MANPATH:$HOME/.config/gcu/man
```

You may want to add these exports to your shell configuration files.

## Course Configuration

After running the installation script, a configuration file will need to be
modifed for the specific course that these utilities will be used for. To modify
the configuration file, run:

```bash
vi $HOME/.config/gcu/config.toml
```

A template configuration file will be supplied during installation if one does
not already exist. The configuration file should have this basic structure:

```toml
canvas_url = "https://canvas.ucsc.edu"
canvas_course_id = 42878
canvas_token = "<your token here>"
course = "cse13s"
quarter = "spring"
year = "2021"
gitlab_server = "https://git.ucsc.edu"
gitlab_token = "<your token here>"
gitlab_role = "developer"
template_repo = "https://git.ucsc.edu/euchou/cse13s-template.git"
```

- `canvas_url`: the Canvas server that your course is hosted on.
- `canvas_course_id`: the Canvas course ID for your course. The one in the
  template is for the Spring 2021 offering of CSE 13S. You can find any course
  ID directly from the course page's url on Canvas.
- `canvas_token`: your Canvas access token as a string. To generate a  Canvas
  token, head to your account settings on Canvas. There will be a button to
  create a new access token under the section titled **Approved Integrations**.
  Note that you must have at least TA-level privilege under the course you want
  to use these scripts with.
- `course`, `quarter`, and `year` should reflect, as one can imagine, the
  course, quarter, and year in which the course is held.
- `gitlab_server`: the GitLab server that you want to create the course group
  and student repos on.
- `gitlab_token`: your GitLab token as a string. Your token should have API-level privilege.
- `gitlab_role`: the default role of students for their individual or shared repositories.
- `template_repo`: the template repository to import and use as a base for
  student repositories. Note that this template repository will need to be
  publically visible.

## Contributing

If you are interested in contributing to these scripts, send an email to
`euchou@ucsc.edu`. Questions are welcomed as well.
