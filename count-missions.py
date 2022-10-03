# count-missions.py

import argparse
from os.path import basename
import sys
from typing import Any
from Paradox_Localisation.utils import generate_localisation
from Simple_Clausewitz import SimpleCWLexer, SimpleCWParser
from Simple_Clausewitz.parser import ParseError

LEXER = SimpleCWLexer()
PARSER = SimpleCWParser()


def make_markdown_table(array: list[Any]) -> str:
    """Generates a Markdown table from a Python list

    Taken from:
    https://gist.github.com/m0neysha/219bad4b02d2008e0154?permalink_comment_id=4201220#gistcomment-4201220

    Made minor change to centralize text by default.

    Args:
        array (list[Any]): a python list.

    Returns:
        str: a string representation of the generated markdown table
    """

    nl = "\n"

    markdown = nl
    markdown += f"| {' | '.join(array[0])} |"

    markdown += nl
    markdown += f"| {' | '.join([':-:']*len(array[0]))} |"

    markdown += nl
    for entry in array[1:]:
        markdown += f"| {' | '.join(entry)} |{nl}"

    markdown += nl

    return markdown


def search_up(file: str) -> str | None:
    from os.path import isdir, dirname, abspath

    if isdir(abspath(file) + "/localisation"):
        return file
    elif file == "/":
        return None
    else:
        return search_up(dirname(abspath(file)))


def walk(
    tree: tuple, in_not: bool, tags: set[str] | None = None
) -> tuple[tuple, bool, set[str]]:
    if tags is None:
        tags = set()

    for elem in tree:
        if elem[0] == "tag" and not in_not:
            tags.add(elem[1])
        if elem[0].upper() == "NOT":
            # We are inside a NOT = { } block
            walk(elem[1], not in_not, tags)
        if any(x == elem[0].upper() for x in ["AND", "OR"]):
            # We are inside either a AND = { } or OR = { }
            walk(elem[1], in_not, tags)

    return (tree, in_not, tags)


def count_missions(files: list) -> dict[str, tuple[int, int, int]]:
    dic: dict[str, tuple[int, int, int]] = dict()
    for file in files:
        try:
            result = PARSER.parse(LEXER.tokenize(file.read()))
        except ParseError as e:
            print("%s: failed to parse: %s" % (basename(file.name), e), file=sys.stderr)
            continue  # Try parsing the other files
        # Some files might be messed up
        except Exception as e:
            print("%s: %s" % (basename(file.name), e), file=sys.stderr)
            continue

        for mission_group in result:
            eligible_tags: set[str] = set()
            for statement in mission_group[1]:
                # Check the "potential = { }" block to see which tags
                # are eligible for the missions
                if statement[0] == "potential":
                    _, _, eligible_tags = walk(statement[1], False, None)

            for statement in mission_group[1]:
                if any(
                    x == statement[0].lower()
                    for x in [
                        "potential",
                        "generic",
                        "ai",
                        "has_country_shield",
                        "slot",
                    ]
                ):
                    continue

                if all(
                    x in dict(statement[1])
                    for x in [
                        "icon",
                        "trigger",
                        "effect",
                    ]
                ):
                    # AB-specific check if the mission
                    # is branching by use of 2 specific
                    # icons, icon_mission_unknown (from origins DLC)
                    # and icon_locked_mission (from Lions of the North DLC)
                    if any(
                        x in dict(statement[1])["icon"]
                        for x in [
                            "mission_unknown_mission",
                            "mission_locked_mission",
                        ]
                    ):
                        for tag in eligible_tags:
                            try:
                                dic[tag] = (
                                    dic[tag][0] + 1,
                                    dic[tag][1],
                                    dic[tag][2] + 1,
                                )
                            except KeyError:
                                dic[tag] = (1, 0, 1)
                    else:
                        for tag in eligible_tags:
                            try:
                                dic[tag] = (
                                    dic[tag][0] + 1,
                                    dic[tag][1] + 1,
                                    dic[tag][2],
                                )
                            except KeyError:
                                dic[tag] = (1, 1, 0)

    return dic


def parse_args(args=None):
    d = "Read list of files and count how many missions a Tag has"
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument(
        "files",
        type=argparse.FileType("r"),
        nargs="+",
        help="list of files to read",
    )
    parser.add_argument(
        "-l",
        "--localise",
        action="store_true",
        default=False,
        help="Localise country TAGs into their names",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Where to output the markdown table",
    )
    parser.add_argument(
        "-d",
        "--extra-dir",
        type=str,
        nargs=1,
        help="extra directories to load localisation from",
    )
    return parser.parse_args(args)


def main(args=None) -> int:
    args = parse_args(args)

    if not args.localise and args.extra_dir is not None:
        print("-d|--extra-dir is useless without -l|--localise", file=sys.stderr)

    final_dict: dict[str, tuple[int, int, int]] = count_missions(args.files)

    final_list: list[list[str]] = []

    search_dirs: set[str] = set()
    localisation = None
    if args.localise:
        if args.extra_dir is not None:
            for dir in args.extra_dir:
                search_dirs.add(dir)
        for file in reversed(args.files):
            dir = search_up(file.name)
            if dir is not None:
                search_dirs.add(dir)

        localisation = generate_localisation(list(search_dirs))

    # Convert it to a list
    for k, v in final_dict.items():
        if localisation is not None:
            # Rewrite the key to include localisation
            k = "%s (%s)" % (localisation[k]["value"][1:-1], k)
        final_list.append([k, str(v[0]), str(v[1]), str(v[2])])
        final_list.sort(key=lambda x: int(x[1]), reverse=True)

    final_list.insert(0, ["Country", "Total", "Normal", "Branching"])

    args.out.write(make_markdown_table(final_list))

    return 0


if __name__ == "__main__":
    sys.exit(main())
