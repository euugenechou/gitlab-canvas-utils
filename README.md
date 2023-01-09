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

A brief description of the provided scripts/utilities:
- `addtorepos` - adds students to a set of specified repositories.
- `checkout` - checks out cloned student repositories to commit IDs submitted for a specific assignment.
- `clone` - clones student repositories.
- `createrepos` - creates course GitLab course and student repos.
- `pushfiles` - adds files to cloned student repositories, pushing the changes.
- `rmfiles` - removes files from cloned student repositories, pushing the changes.
- `rmfromrepos` - removes students from a set of specified repositories
- `roster` - scrapes Canvas for a CSV of the student roster.

Read the supplied `man` pages for more information on each of these utilities.

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

Running the installation script will add a template configuration file under
the following path:

```bash
vi $HOME/.config/gcu/config.toml
```

The template configuration file should be copied, modified, and used on a
per-course basis. It is recommended to have a directory of configuration files
if you have multiple courses to manage. A valid configuration file contains the
following fields:

```toml
canvas_url = "https://canvas.ucsc.edu"
canvas_course_id = 42878
canvas_token = "<your token here>"
base_repo_path = "cse13s/winter2023/section01"
gitlab_server = "https://git.ucsc.edu"
gitlab_token = "<your token here>"
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
- `base_repo_path`: the base repo path that student repos should be created
  under. The first component of the path should generally be the course, and
  subsequent components are the nested subgroups. An example of a base repo path
  without a section subgroup: `cse13s/winter2023`.
- `gitlab_server`: the GitLab server that you want to create the course group
  and student repos on.
- `gitlab_token`: your GitLab token as a string. Your token should have API-level privilege.
- `template_repo`: the template repository to import and use as a base for
  student repositories. Note that this template repository will need to be
  publically visible and *must* be supplied an HTTP URL, not SSH.

To specify which config to use, simply set a `GCU_CONFIG` environment variable
before running any of the provided scripts/utilities. The following example
command pipelines only have `GCU_CONFIG` set for the respective pipeline so as to
not pollute the environment variable namespace, but using `export` and/or `env`
are viable approaches as well. Having `GCU_CONFIG` set per command pipeline is
handy if you happen to be managing several classes concurrently.

##### Creating GitLab course, student repos, and adding students to resources repository

```bash
$ GCU_CONFIG=<path to config> bash -c "roster | createrepos | addtorepos <resource repo id>"
```
##### Cloning all student repos and checking them out to submitted commit IDs

```bash
$ GCU_CONFIG=<path to config> bash -c "roster | clone | checkout --asgn=5"
```

## Contributing

If you are interested in contributing to these scripts, send an email to
`euchou@ucsc.edu`. Questions are welcomed as well.
