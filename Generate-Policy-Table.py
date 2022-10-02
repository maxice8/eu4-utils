# ReadIdeas.py

import argparse
import io
import os
from Simple_Clausewitz import SimpleCWLexer, SimpleCWParser
import sys
from typing import Any

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


def is_group_idea(idea_group: tuple[str, list[Any]]) -> str | None:
    """Checks if a tuple is a Group Idea by checking if they have a
    category field with a valid monarch power point

    Args:
        idea_group (tuple[str, list[Any]]): Tuple representing the Idea Group

    Returns:
        str | None: If the tuple is a Group Idea then return
        its name, otherwise return none
    """
    # First element is the name, the second is a list
    elements = idea_group[1]

    for elem in elements:
        # Check if we have a (Category, {ADM,DIL,MIL}) tuple.
        if elem[0] == "category":
            if elem[1] == "ADM" or "DIP" or "MIL":
                return idea_group[0]

    return None


def read_all_files_in_dir(dir: str) -> str:
    """Read all Files in a directory and return as a string

    Args:
        dir (str): path, relative or absolute, to the directory

    Returns:
        str: all the files in dir, concatenated with a newline of separation
    """
    wfd = io.StringIO()
    for file in os.listdir(dir):
        with open(f"{dir}/{file}", "r") as fd:
            wfd.write(fd.read())
            wfd.write("\n")

    return wfd.getvalue()


def generate_policy_list(dir) -> dict[str, list[str]]:
    """Generates a dictionary of defined policies returning a dictionary
    with all policies and what ideas one must have. Assumes ideas found
    via potential = { has_idea_group = <idea> } are the only requirements

    Args:
        dir (_type_): path to the mod directory

    Returns:
        dict[str, list[str]]: Dictionary with the keys named after
        policies, the value of a key is a list of ideas that are required
    """
    stream = read_all_files_in_dir(f"{dir}/common/policies")
    result = PARSER.parse(LEXER.tokenize(stream))

    # Map the policies into a Dictionary with list, and have
    # the ideas we are testing for intersection.
    Policies: dict[str, list[str]] = dict()

    for policy in result:
        # policy_name
        policy_name = policy[0]

        # The second element (index 1) of the tuplet is a list
        # of everything inside it, check it for potential
        for element in policy[1]:
            if element[0] != "potential":
                continue

            for elem in element[1]:
                if elem[0] == "has_idea_group":
                    # If the key does not exist, create it
                    if policy_name not in Policies:
                        Policies[policy_name] = list()

                    # Then append to it
                    Policies[policy_name].append(elem[1])

            # Check only the first time
            break

    return Policies


def parse_args(args=None):
    d = "Read Group Ideas and Policies and generate a Markdown table"
    parser = argparse.ArgumentParser(description=d)
    parser.add_argument(
        "moddir",
        type=str,
        help="Mod directory to read",
    )
    parser.add_argument(
        "-l",
        "--localise",
        default=False,
        action="store_true",
        help="Localise the ideas and policies in the table",
    )
    parser.add_argument(
        "-b",
        "--base",
        type=str,
        default=None,
        nargs=1,
        help="Location of base game, used for any missing localisation",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Where to output the markdown table",
    )
    return parser.parse_args(args)


def main(args=None) -> int:
    args = parse_args(args)
    moddir = args.moddir

    if args.base is not None:
        if args.localise is False:
            print("-b|--base is useless without -l|--localise", file=sys.stderr)

    # Switch to the path given to us
    try:
        os.chdir(moddir)
    except FileNotFoundError:
        print("%s: does not exist" % moddir, file=sys.stderr)
        return 1
    except PermissionError:
        print("%s: permission denied" % moddir, file=sys.stderr)
        return 1
    except NotADirectoryError:
        print("%s: not a directory" % moddir, file=sys.stderr)
        return 1
    except OSError as e:
        print("%s: %s" % (moddir, e), file=sys.stderr)
        return 1

    # Copy all files from the ideas folder
    stream = read_all_files_in_dir("common/ideas")
    result = PARSER.parse(LEXER.tokenize(stream))

    # The result is a List of all tuples, let's parse it.
    Group_Ideas: list[str] = [
        "",
    ]
    for idea in result:
        ret = is_group_idea(idea)
        if ret is not None:
            Group_Ideas.append(ret)

    # Get number of ideas, reduce the length by one as the first
    # row is a '-'
    num_of_ideas = len(Group_Ideas) - 1

    # Create a matrix that will be converted into a markdown table
    # format:
    # [[- 1 2 3 4 5]
    #  [1 - b c d e]
    #  [2 a - c d e]
    #  [3 a b - d e]
    #  [4 a b c - e]
    #  [5 a b c d -]]
    Idea_Table: list[list] = [[]]

    # Re-use the extracted group ideas from the first row
    Idea_Table[0] = Group_Ideas

    # Get all the policies
    policies = generate_policy_list(sys.argv[1])

    # Skip the first element as it is a '-' and we only
    # want it for the top-most left field
    for index, idea in enumerate(Group_Ideas[1:]):
        table_row: list[str] = [idea]
        i = 0
        while i < num_of_ideas:
            if i == index:
                table_row.append(" - ")
            elif (
                # Ante-Bellum specific as the Global Domination ideas
                # has no policies as intended
                Group_Ideas[i + 1] == "globaldomination_ideas"
                or idea == "globaldomination_ideas"
            ):
                table_row.append("No Policies by Design")
            else:
                has_found_policy = False
                # Check if we can find a policy, and map it to the table
                for key, values in policies.items():
                    # Add 1 as we index over 0 and we need to catch up
                    if idea in values and Group_Ideas[i + 1] in values:
                        has_found_policy = True
                        table_row.append(key)

                # If we can't find a policy
                if not has_found_policy:
                    table_row.append("missing")

            i += 1

        Idea_Table.append(table_row)

    # Localise
    if args.localise:
        # Helper function to generate dictionary mapping keys
        # to values and versions
        from Paradox_Localisation import generate_localisation

        localisation = generate_localisation(moddir, extra_dirs=args.base)

        # Run over all the values of the table and replace them.
        for idx, x in enumerate(Idea_Table):
            for idy, y in enumerate(x):
                if y in localisation:
                    # The [1:-1] is to remove the double-quotes
                    Idea_Table[idx][idy] = localisation[y]["value"][1:-1]

    args.out.write(make_markdown_table(Idea_Table))
    return 0


if __name__ == "__main__":
    sys.exit(main())
