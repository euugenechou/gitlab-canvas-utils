#!/usr/bin/python3

import csv, re, sys, json, gitlab, subprocess, argparse, logging

SERVER = "https://git.ucsc.edu"
DOMAIN = "ucsc.edu"

repo_ops = {
    "access_created": 0,
    "access_updated": 0,
    "access_removed": 0,
    "newrepo": 0,
    "nouser": 0,
    "error": 0
}

roles = {
    "developer": gitlab.DEVELOPER_ACCESS,
    "maintainer": gitlab.MAINTAINER_ACCESS,
    "owner": gitlab.OWNER_ACCESS,
    "reporter": gitlab.REPORTER_ACCESS
}

def validate_config(config):
    if "server" not in config:
        config["server"] = SERVER
    if "gitlab_token" not in config:
        raise ValueError("missing GitLab token.")
    if "course" not in config:
        raise ValueError("missing course.")
    if "quarter" not in config:
        raise ValueError("missing quarter.")
    if "year" not in config:
        raise ValueError("missing year.")
    if "template_repo" not in config:
        raise ValueError("missing template repo to import.")
    if "gitlab_role" not in config:
        raise ValueError("missing student repo role.")
    if config["gitlab_role"] not in roles:
        raise ValueError("invalid student repo role.")

def create_repo(gl, group, name, users, role, template_repo, remove_unlisted):
    fullname = group.full_path + "/" + name

    try:
        # Try creating the repo.
        repo = gl.projects.create({
            "name": name,
            "namespace_id": group.id,
            "visibility": "private",
            "lfs_enabled": False,
            "import_url": template_repo
        })
        logging.info(f"{fullname}: repo created.")
        repo_ops["newrepo"] += 1
    except:
        # Maybe the repo already exists?
        try:
            repo = gl.projects.get(fullname)
        except:
            logging.error(f"{fullname}: error creating or finding repo.")
            repo_ops["error"] += 1
            return

    curr_members = repo.members.list()
    allowed_users = []

    for username in users:
        try:
            # Find user and add to list of allowed users.
            user = gl.users.list(username=username)[0]
            allowed_users.append(user.id)
        except:
            # User doesn't exist.
            logging.warning(f"{fullname}: user {username} doesn\'t (yet) exist... skipping.")
            repo_ops["nouser"] += 1
            continue

        if user.id not in [member.id for member in curr_members]:
            try:
                member = repo.members.create({
                    "user_id": user.id,
                    "access_level": roles[role]
                })
                repo_ops["access_created"] += 1
            except:
                logging.error(f"{fullname}: unable to add {username} for access.")
                repo_ops["error"] += 1

        try:
            member = repo.members.get(user.id)
            member.access_level = roles[role]
            member.save()
            logging.info(f"{fullname}: {username} given {role} access.")
            repo_ops["access_updated"] += 1
        except:
            logging.error(f"{fullname}: {username} not given {role} access.")
            repo_ops["error"] += 1

    if remove_unlisted:
        for member in curr_members:
            if member.id not in allowed_users:
                try:
                    member.delete()
                    logging.info(f"{fullname}: {member.username} removed as {role}.")
                    repo_ops["access_removed"] += 1
                except:
                    logging.error(f"{fullname}: unable to remove {role} access for {member.username}.")
                    repo_ops["error"] += 1

def create_individual_repos(csvfile, gl, group, template_repo, role):
    reader = csv.reader(csvfile, delimiter=',')
    for _, _, cruzid, _, in reader:
        create_repo(gl, group, cruzid, [cruzid], role, template_repo, False)

def create_shared_repos(csvfile, gl, group, template_repo, role, remove_unlisted):
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if len(row) > 1:
            groupname, cruzids = row[0], row[1:]
            create_repo(gl, group, groupname, cruzids, role, template_repo, remove_unlisted)
        else:
            logging.error(f"{row[0]}: no users specified for shared repo")

def group_search(user, path):
    for group in user.groups.list():
        if group.full_path == path:
            return group
    logging.warning(f"{path}: group not found.")
    return None

def subgroup_search(user, group, path):
    for subgroup in user.groups.list():
        if subgroup.path == path and subgroup.parent_id == group.id:
            return subgroup
    logging.warning(f"{group.full_path}/{path}: subgroup not found.")
    return None

def group_check(user, course):
    group = group_search(user, course)
    group_name = course.upper()

    if not group:
        user.groups.create({
            'name': group_name,
            'path': path,
        })

        while not group:
            group = group_search(user, path)

        logging.info(f"{group.full_path}: group created.")

    settings = group.notificationsettings.get()
    settings.level = gitlab.NOTIFICATION_LEVEL_DISABLED
    settings.save()
    logging.info(f"{group.full_path}: group notifications disabled.")
    return group

def subgroup_check(user, group, quarter, year):
    path = quarter + year
    subgroup = subgroup_search(user, group, path)
    subgroup_name = quarter.capitalize() + " " + year

    if not subgroup:
        user.groups.create({
            'name': subgroup_name,
            'path': path,
            'parent_id': group.id
        })

        while not subgroup:
            subgroup = subgroup_search(user, group, path)

        logging.info(f"{subgroup.full_path}: subgroup created.")

    settings = subgroup.notificationsettings.get()
    settings.level = gitlab.NOTIFICATION_LEVEL_DISABLED
    settings.save()
    logging.info(f"{subgroup.full_path}: subgroup notifications disabled.")

    return subgroup

def course_check(user, course, quarter, year):
    group = group_check(user, course)
    return subgroup_check(user, group, quarter, year)

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Creates GitLab repos for students in a course given a CSV.\n"
            "Will also create the couse group and quarter subgroup.\n"
            "Supports the creation of both individual repos and shared repos.\n"
            "Each row in the CSV must be formatted as: name, CanvasID, CruzID, repo."
        )
    )
    parser.add_argument(
        "-c", "--csv", nargs="?", default=None,
        help="the CSV containing the list of students to create repos for."
    )
    parser.add_argument(
        "-s", "--shared", default=False, action="store_true",
        help="create shared repos for students instead of individual repos"
    )
    parser.add_argument(
        "-r", "--remove-unlisted", default=False, action="store_true",
        help="remove unlisted members from group repos."
    )
    parser.add_argument(
        "-v", "--verbose", default=False, action="store_true",
        help="print verbose statistics to stderr"
    )
    parser.add_argument(
        "-l", "--logging-level", default="INFO",
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help="set logging level."
    )
    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stderr, level=args.logging_level.upper(),
        format='[%(levelname)s] %(message)s'
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
        logging.error("invalid GitLab token.")
        sys.exit(1)

    # Validate the template repo to import.
    try:
        subprocess.check_call(["git", "ls-remote", config["template_repo"]],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        logging.error("unable to import template repo.")
        sys.exit(1)

    # Check if group and subgroup for class exist, create if they don't.
    try:
        course = course_check(user, config["course"], config["quarter"], config["year"])
    except:
        logging.error("unable to find or create GitLab course.")
        sys.exit(1)

    # Use stdin as default input to read CSV from.
    csvfile = open(args.csv, "r") if args.csv else sys.stdin

    # Unpack some config parameters.
    template_repo = config["template_repo"]
    gitlab_role = config["gitlab_role"]

    # Repos are either shared or not shared at this point.
    if args.shared:
        create_shared_repos(csvfile, user, course, template_repo, gitlab_role, args.remove_unlisted)
    else:
        create_individual_repos(csvfile, user, course, template_repo, gitlab_role)

    # Print statistics of repo creation.
    if args.verbose:
        print('Overall statistics:', file=sys.stderr)
        for k in sorted(repo_ops.keys()):
            print(f" - {k}: {repo_ops[k]}", file=sys.stderr)

if __name__ == "__main__":
    main()
