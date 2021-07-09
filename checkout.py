#!/usr/bin/python3

from canvasapi import Canvas
from git import Repo, GitCommandError, InvalidGitRepositoryError
import argparse, csv, json, logging, os, re, sys

def get_assignment(canvas_course, asgn_num):
    '''
    Returns the specified assignment object.
    Note: this ignores assignments on Canvas for DESIGN.pdf submissions (if applicable).
    '''
    for asgn in canvas_course.get_assignments():
        if f"Assignment {asgn_num}" in asgn.name and "DESIGN" not in asgn.name:
            return asgn
    return None

def get_commit_id(cruz_id, body):
    '''
    Returns the submitted commit ID in the Canvas text-entry box.
    '''
    match = re.search(r"\b([a-fA-F0-9]{8,40})\b", body)
    if match:
        return match.group(1)
    return None

def checkout_assignment_repos(canvas_course, csvfile, repodir, asgn_num):
    '''
    Checks out each student repo in the CSV file.
    Only repos that have been cloned already will be checked out.
    The commit that is checked out is the one submitted on Canvas for the assignment.
    '''
    if not os.path.exists(repodir):
        logging.error(f"{repodir}: directory not found")
        return

    asgn = get_assignment(canvas_course, asgn_num)
    if not asgn:
        logging.error(f"assignment {asgn_num} not found")
        return

    reader = csv.reader(csvfile, delimiter=',')
    for _, canvasid, cruzid, repo in reader:
        repopath = os.path.join(repodir, cruzid)

        try:
            submission = asgn.get_submission(canvasid)
        except Exception as e:
            logging.error(f"{cruzid}: assignment submission error")
            failed_checkouts.append((cruzid, err))
            continue

        if os.path.exists(repopath) and submission.submitted_at:
            repoclone = Repo(repopath)

            commit_id = get_commit_id(cruzid, submission.body)
            if not commit_id:
                logging.error(f"{cruzid}: invalid or missing commit ID submission")
                continue

            try:
                repoclone.git.checkout(commit_id)
                logging.info(f"{cruzid}: checked out commit {commit_id}")
            except (ValueError, GitCommandError) as err:
                logging.error(f"{cruzid}: failed to check out {commit_id}: {err}")

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Checks out cloned student repos to the commit IDs submitted on Canvas.\n"
            "Takes in a CSV where each row is formatted as: name, CanvasID, CruzID, repo.\n"
            "A specific CSV can be specified via commandline option (default: stdin).\n"
            "The repos are assumed to have been cloned using the cloner.py script.\n"
            "Unless otherwise specified, the repos are assumed to be cloned under /tmp/repos/."
        )
    )
    parser.add_argument(
        "-a", "--asgn", nargs="?", required=True,
        help="the assignment number to clone repos and checkout code for."
    )
    parser.add_argument(
        "-c", "--csv", nargs="?", default=None,
        help="the CSV containing the repos to clone."
    )
    parser.add_argument(
        "-l", "--logging-level", default="INFO",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help="set logging level for logs to stderr (default: info)."
    )
    parser.add_argument(
        "-r", "--repodir", nargs="?", default="/tmp/repos",
        help="the directory to contain the cloned repos (default: /tmp/repos)."
    )
    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stderr, level=args.logging_level.upper(),
        format='[%(levelname)s] %(message)s'
    )

    # Disable canvasapi logging.
    canvas_logger = logging.getLogger("canvasapi")
    canvas_logger.propagate = False

    with open("config.json", "r") as configfile:
        config = json.load(configfile)

        canvas_url = config["canvas_url"]
        canvas_course_id = config["canvas_course_id"]
        token = config["canvas_token"]

        canvas = Canvas(canvas_url, token)
        canvas_course = canvas.get_course(canvas_course_id)

    csv = open(args.csv, "r") if args.csv else sys.stdin
    checkout_assignment_repos(canvas_course, csv, args.repodir, args.asgn)

if __name__ == "__main__":
    main()
