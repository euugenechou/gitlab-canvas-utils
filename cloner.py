#!/usr/bin/python3

from canvasapi import Canvas
from collections import namedtuple
from git import Repo, GitCommandError, InvalidGitRepositoryError
import argparse, csv, json, logging, os, shutil, sys
import subprocess as sp

def clone_repos(csvfile, repodir, forward):
    '''
    Clones each student repo in the CSV file.
    Repos that have already been cloned are pulled from instead.
    Repos are cloned into the specified directory.
    '''
    if not os.path.exists(repodir):
        os.makedirs(repodir)

    reader = csv.reader(csvfile, delimiter=',')
    writer = csv.writer(sys.stdout, delimiter=",")

    for row in reader:
        _, _, cruzid, repo = row
        repopath = os.path.join(repodir, cruzid)

        if not os.path.exists(repopath):
            try:
                repo_clone = Repo.clone_from(repo, repopath)
                if forward:
                    writer.writerow(row)
                logging.info(f"{cruzid}: successfully cloned repo")
            except (GitCommandError, InvalidGitRepositoryError) as err:
                logging.error(f"{cruzid}: failed to clone repo: {err}")
        else:
            try:
                repo_clone = Repo(repopath)
                repo_clone.git.checkout("master")
                repo_clone.git.pull()
                if forward:
                    writer.writerow(row)
                logging.info(f"{cruzid}: successfully pulled repo")
            except (GitCommandError, InvalidGitRepositoryError) as err:
                logging.error(f"{cruzid}: failed to pull repo: {err}")

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Clones student repos given a CSV.\n"
            "Each row in the CSV must be formatted as: name, CanvasID, CruzID, repo."
        )
    )
    parser.add_argument(
        "-c", "--csv", nargs="?", default=None,
        help="the CSV containing the repos to clone."
    )
    parser.add_argument(
        "-r", "--repodir", nargs="?", default="/tmp/repos",
        help="the directory to contain the cloned repos (default: /tmp/repos)."
    )
    parser.add_argument(
        "-f", "--forward", default=False, action="store_true",
        help="send the CSV rows for the students whose repos were cloned/pulled to stdout"
    )
    parser.add_argument(
        "-l", "--logging-level", default="INFO",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help="set logging level for logs to stderr (default: info)."
    )
    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stderr, level=args.logging_level.upper(),
        format='[%(levelname)s] %(message)s'
    )

    # Use stdin as default input to read CSV from.
    csvfile = open(args.csv, "r") if args.csv else sys.stdin
    clone_repos(csvfile, args.repodir, args.forward)

if __name__ == "__main__":
    main()
