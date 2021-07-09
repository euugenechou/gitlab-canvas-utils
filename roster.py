#!/usr/bin/python3

from canvasapi import Canvas
import argparse, csv, json, os, re, sys

def create_student_csv(course, outfile, base_gitlab_url, start, end):
    '''
    Writes the course student roster as a CSV file.
    Each row formatted as: name, CanvasID, CruzID, repo.
    '''
    students = []

    # Special attention required when getting CruzID (some people have + in the email).
    for user in course.get_users(enrollment_type=['student'], enrollment_state=['active']):
        name = user.sortable_name
        canvas_id = user.id
        email = user.email
        cruzid = re.search(r'(.*?)(\+.*?)?@ucsc.edu', email).group(1)
        repo = os.path.join(base_gitlab_url, f"{cruzid}.git")
        students.append((name, canvas_id, cruzid, repo))

    # We start writing when we reach the start CruzID.
    # If there isn't a specified start, we write immediately.
    write = True if not start else False

    # Sort students by name in increasing lexographic order, then write them out.
    students.sort(key=lambda s: s[0])
    writer = csv.writer(outfile, delimiter=",")
    for name, canvas_id, cruzid, repo in students:
        # If we reach the start, we know to start writing.
        # Having the check for end after writing allows the end CruzID to be written as well.
        if cruzid == start:
            write = True
        if write:
            writer.writerow([name, canvas_id, cruzid, repo])
        if cruzid == end:
            write = False
            break # We know we're done at this point.

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Generates CSV of entire CSE 13S Canvas roster in lexographic order.\n"
            "This ordering applies when restricting to range of students by CruzID.\n"
            "This is by design because CruzIDs are easier to enter than full names.\n"
            "Each row in the CSV is formatted as: name, CanvasID, CruzID, repo."
        )
    )
    parser.add_argument(
        "-o", "--outfile", nargs="?", default=None,
        help="Output for generated CSV (default: stdout)."
    )
    parser.add_argument(
        "-s", "--start", nargs="?", default=None,
        help="first CruzID to start CSV output from."
    )
    parser.add_argument(
        "-e", "--end", nargs="?", default=None,
        help="last CruzID to end CSV output with."
    )
    parser.add_argument(
        "-r", "--range", nargs="?", default=None,
        help="range of CruzID to output (ex: --range=start,end)."
    )
    args = parser.parse_args()

    # Write CSV to stdout by default.
    outfile = open(args.outfile, "w") if args.outfile else sys.stdout

    with open("config.json", "r") as configfile:
        config = json.load(configfile)

        canvas_url = config["canvas_url"]
        canvas_course_id = config["canvas_course_id"]
        canvas_token = config["canvas_token"]
        course = config["course"]
        quarter = config["quarter"]
        year = config["year"]

        canvas = Canvas(canvas_url, canvas_token)
        canvas_course = canvas.get_course(canvas_course_id)

    # This assumes that the GitLab project is created using the repocreator script.
    # Otherwise, the base GitLab url will change.
    base_gitlab_url = f"git@git.ucsc.edu:{course}/{quarter}{year}/"

    # Some basic parsing of the range option.
    start = args.start
    end = args.end
    if args.range:
        idrange = args.range.split(',')
        start, end = idrange[0], idrange[1]

    create_student_csv(canvas_course, outfile, base_gitlab_url, start, end)

if __name__ == "__main__":
    main()
