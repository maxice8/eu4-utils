# count-missions.py

import argparse
import sys
from os.path import basename
from typing import Any

from Paradox_Localisation.utils import generate_localisation
from Simple_Clausewitz import SimpleCWLexer, SimpleCWParser, ParseError
from hw_utils import make_markdown_table, has_mapping

LEXER = SimpleCWLexer()
PARSER = SimpleCWParser()

ANTE_BELLUM: bool = False


def add_normal_mission(dic: dict[str, tuple[int, int, int]], tag: str):
    try:
        dic[tag] = (
            dic[tag][0] + 1,
            dic[tag][1] + 1,
            dic[tag][2],
        )
    except KeyError:
        dic[tag] = (1, 1, 0)


def add_branching_mission(dic: dict[str, tuple[int, int, int]], tag: str):
    try:
        dic[tag] = (
            dic[tag][0] + 1,
            dic[tag][1],
            dic[tag][2] + 1,
        )
    except KeyError:
        dic[tag] = (1, 0, 1)


def search_up(file: str) -> str | None:
    from os.path import abspath, dirname, isdir

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
            potential_statement: tuple[str, Any]
            for statement in mission_group[1]:
                # Check the "potential = { }" block to see which tags
                # are eligible for the missions
                if statement[0] == "potential":
                    potential_statement = statement[1]
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
                            if ANTE_BELLUM:
                                # Check for Golden Horde branches
                                if tag == "GLH" and has_mapping(
                                    potential_statement,
                                    ("has_country_flag", "glh_european_tree"),
                                ):
                                    add_branching_mission(dic, (tag + "+European Path"))
                                    continue
                                if tag == "GLH" and has_mapping(
                                    potential_statement,
                                    ("has_country_flag", "glh_horde_tree"),
                                ):
                                    add_branching_mission(dic, (tag + "+Horde Path"))
                                    continue
                                if tag == "YUA" and has_mapping(
                                    potential_statement,
                                    ("has_country_flag", "YUA_HORDE"),
                                ):
                                    add_branching_mission(dic, (tag + "+Horde Path"))
                                    continue
                                if tag == "YUA" and has_mapping(
                                    potential_statement,
                                    (
                                        "NOT",
                                        [
                                            ("has_country_flag", "YUA_HORDE"),
                                            ("has_country_flag", "YUA_NESTORIAN"),
                                        ],
                                    ),
                                ):
                                    add_branching_mission(
                                        dic, (tag + "+Sinicized Path")
                                    )
                                    continue
                                if tag == "YUA" and has_mapping(
                                    potential_statement,
                                    ("religion", "nestorian"),
                                ):
                                    add_branching_mission(
                                        dic, (tag + "+Nestorian Path")
                                    )
                                    continue
                                if tag == "RUM" and has_mapping(
                                    potential_statement,
                                    ("religion_group", "christian"),
                                ):
                                    add_branching_mission(
                                        dic, (tag + "+Christian Path")
                                    )
                                    continue
                                if tag == "RUM" and has_mapping(
                                    potential_statement, ("religion_group", "muslim")
                                ):
                                    add_branching_mission(dic, (tag + "+Muslim Path"))
                                    continue
                                if tag == "RUM" and has_mapping(
                                    potential_statement, ("religion", "zoroastrian")
                                ):
                                    add_branching_mission(
                                        dic, (tag + "+Zoroastrian Path")
                                    )
                                    continue

                            add_branching_mission(dic, tag)
                    else:
                        for tag in eligible_tags:
                            if ANTE_BELLUM:
                                # Check for Golden Horde branches
                                if tag == "GLH" and has_mapping(
                                    potential_statement,
                                    ("has_country_flag", "glh_european_tree"),
                                ):
                                    add_normal_mission(dic, (tag + "+European Path"))
                                    continue
                                if tag == "GLH" and has_mapping(
                                    potential_statement,
                                    ("has_country_flag", "glh_horde_tree"),
                                ):
                                    add_normal_mission(dic, (tag + "+Horde Path"))
                                    continue
                                if tag == "YUA" and has_mapping(
                                    potential_statement,
                                    ("has_country_flag", "YUA_HORDE"),
                                ):
                                    add_normal_mission(dic, (tag + "+Horde Path"))
                                    continue
                                if tag == "YUA" and has_mapping(
                                    potential_statement,
                                    (
                                        "NOT",
                                        [
                                            ("has_country_flag", "YUA_HORDE"),
                                            ("has_country_flag", "YUA_NESTORIAN"),
                                        ],
                                    ),
                                ):
                                    add_normal_mission(dic, (tag + "+Sinicized Path"))
                                    continue
                                if tag == "YUA" and has_mapping(
                                    potential_statement,
                                    ("religion", "nestorian"),
                                ):
                                    add_normal_mission(dic, (tag + "+Nestorian Path"))
                                    continue
                                if tag == "RUM" and has_mapping(
                                    potential_statement,
                                    ("religion_group", "christian"),
                                ):
                                    add_normal_mission(dic, (tag + "+Christian Path"))
                                    continue
                                if tag == "RUM" and has_mapping(
                                    potential_statement, ("religion_group", "muslim")
                                ):
                                    add_normal_mission(dic, (tag + "+Muslim Path"))
                                    continue
                                if tag == "RUM" and has_mapping(
                                    potential_statement, ("religion", "zoroastrian")
                                ):
                                    add_normal_mission(dic, (tag + "+Zoroastrian Path"))
                                    continue

                            add_normal_mission(dic, tag)

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
    parser.add_argument(
        "--lang",
        "--language",
        type=str,
        default=None,
        help="language for the localisation",
    )
    parser.add_argument(
        "-ab",
        "--ante-bellum",
        action="store_true",
        default=False,
        help="enable Ante-Bellum specific code handling",
    )
    return parser.parse_args(args)


def main(args=None) -> int:
    args = parse_args(args)

    if args.ante_bellum:
        # We were passed --ante-bellum, enable ANTE_BELLUM specific
        # code handling
        global ANTE_BELLUM
        ANTE_BELLUM = True

    if not args.localise:
        if args.extra_dir is not None:
            print("-d|--extra-dir is useless without -l|--localise", file=sys.stderr)
        if args.lang is not None:
            print("--lang|--language is useless without -l|--localise", file=sys.stderr)
        else:
            args.lang = "english"

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

        localisation = generate_localisation(list(search_dirs), language=args.lang)

    # Convert it to a list
    for k, v in final_dict.items():
        if localisation is not None:
            # Replace the '+String' in the localisation
            if "+" in k:
                klist = k.split("+")
                k = "%s (%s) (%s)" % (
                    localisation[klist[0]]["value"][1:-1],
                    klist[1],
                    klist[0],
                )
            else:
                # Rewrite the key to include localisation
                k = "%s (%s)" % (localisation[k]["value"][1:-1], k)

        final_list.append([k, str(v[0]), str(v[1]), str(v[2])])
        final_list.sort(key=lambda x: int(x[1]), reverse=True)

    final_list.insert(0, ["Country", "Total", "Normal", "Branching"])

    args.out.write(make_markdown_table(final_list))

    return 0


if __name__ == "__main__":
    sys.exit(main())
