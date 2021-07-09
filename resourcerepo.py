#!/usr/bin/python3

import csv, re, sys, json, gitlab, subprocess, argparse, logging

SERVER = "https://git.ucsc.edu"

repo_ops = {
    "access_created": 0,
    "access_updated": 0,
    "nouser": 0,
    "error": 0
}

def validate_config(config):
    if "server" not in config:
        config["server"] = SERVER
    if "gitlab_token" not in config:
        raise ValueError("missing GitLab token")
    if "resource_repo_id" not in config:
        raise ValueError("missing project ID of resource repo to add users to.")

def add_user(gl, repo, username):
    try:
        # Find user and add to list of allowed users.
        user = gl.users.list(username=username)[0]
    except:
        # User doesn't exist.
        logging.warning(f"user {username} doesn\'t (yet) exist... skipping.")
        repo_ops["nouser"] += 1
        return

    if not repo.members.list(query=username) and not repo.members.all(query=username):
        try:
            member = repo.members.create({
                "user_id": user.id,
                "access_level": gitlab.REPORTER_ACCESS
            })
            logging.info(f"{username} added as reporter.")
            repo_ops["access_created"] += 1
        except:
            logging.error(f"unable to add {username} for access.")
            repo_ops["error"] += 1
    else:
        try:
            member = repo.members.all(query=username)[0]
            if member.access_level != gitlab.REPORTER_ACCESS:
                if member.access_level > gitlab.REPORTER_ACCESS:
                    logging.warning(f"{username} has higher access than reporter.")
                    return
                member.access_level = gitlab.REPORTER_ACCESS
                member.save()
                logging.info(f"{username} given reporter access.")
                repo_ops["access_updated"] += 1
            else:
                logging.info(f"{username} is already a reporter.")
        except:
            logging.error(f"{username} not given reporter access.")
            repo_ops["error"] += 1

def add_users(csvfile, gl, repo):
    reader = csv.reader(csvfile, delimiter=',')
    for _, _, cruzid, _ in reader:
        add_user(gl, repo, cruzid)

def repo_search(user, project_id):
    repo = user.projects.get(project_id)
    if not repo:
        raise ValueError
    return repo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--csv", nargs="?", default=None,
        help="File path of course config file."
    )
    parser.add_argument(
        "-v", "--verbose", default=False, action="store_true",
        help="File path of course config file."
    )
    parser.add_argument(
        "-l", "--logging-level", default="INFO",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help="Set logging level."
    )
    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stderr, level=args.logging_level.upper(),
        format="[%(levelname)s] %(message)s"
    )

    # Load the configuration.
    with open("config.json", "r") as configfile:
        config = json.load(configfile)

    # Validate the configuration.
    try:
        validate_config(config)
    except ValueError as err:
        logging.error(err)
        sys.exit(1)

    # Authenticate the token.
    try:
        user = gitlab.Gitlab(config["server"], config["gitlab_token"], api_version=4)
        user.auth()
    except:
        logging.error("invalid GitLab token")
        sys.exit(1)

    # Find the resource repo.
    try:
        resource_repo = repo_search(user, config["resource_repo_id"])
    except:
        logging.error("invalid resource repo ID")
        repo_ops["error"] += 1
        sys.exit(1)

    csvfile = open(args.csv, "r") if args.csv else sys.stdin
    add_users(csvfile, user, resource_repo)

    # Print statistics of adding students to resource repo.
    if args.verbose:
        print('Overall statistics:', file=sys.stderr)
        for k in sorted(repo_ops.keys()):
            print(f" - {k}: {repo_ops[k]}", file=sys.stderr)

if __name__ == "__main__":
    main()
