# ReadIdeas.py

import io
import os
from shutil import copyfileobj
import shutil
from Simple_LexParser import SimpleClausewitzLexer, SimpleClausewitzParser
import sys
from typing import Optional, Tuple, Any, List


def make_markdown_table(array):
    """the same input as above"""

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


def is_group_idea(idea_group: Tuple[str, List[Any]]) -> Optional[str]:
    # First element is the name, the second is a list
    elements = idea_group[1]

    for elem in elements:
        # Check if we have a (Category, {ADM,DIL,MIL}) tuple.
        if elem[0] == "category":
            if elem[1] == "ADM" or "DIP" or "MIL":
                return idea_group[0]

    return None


def read_all_files_in_dir(dir: str) -> str:
    wfd = io.StringIO()
    for file in os.listdir(dir):
        with open(f"{dir}/{file}", "r") as fd:
            wfd.write(fd.read())
            wfd.write("\n")

    return wfd.getvalue()


def generate_policy_list(dir) -> dict[str, list[str]]:
    lexer = SimpleClausewitzLexer()
    parser = SimpleClausewitzParser()

    stream = read_all_files_in_dir(f"{dir}/common/policies")
    result = parser.parse(lexer.tokenize(stream))

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
                    if not policy_name in Policies:
                        Policies[policy_name] = list()

                    # Then append to it
                    Policies[policy_name].append(elem[1])

            # Check only the first time
            break

    return Policies


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(99)

    os.chdir(sys.argv[1])

    lexer = SimpleClausewitzLexer()
    parser = SimpleClausewitzParser()

    # Copy all files from the ideas folder
    stream = read_all_files_in_dir("common/ideas")
    result = parser.parse(lexer.tokenize(stream))

    # The result is a List of all tuples, let's parse it.
    Group_Ideas: List[str] = [
        "-",
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
    Idea_Table: List[List] = [[]]

    # Re-use the extracted group ideas from the first row
    Idea_Table[0] = Group_Ideas

    # Get all the policies
    policies = generate_policy_list(sys.argv[1])

    # Skip the first element as it is a '-' and we only
    # want it for the top-most left field
    for index, idea in enumerate(Group_Ideas[1:]):
        table_row: List[str] = [idea]
        i = 0
        while i < num_of_ideas:
            if i == index:
                table_row.append(" - ")
            else:
                has_found_policy = False
                # Check if we can find a policy, and map it to the table
                for key, values in policies.items():
                    # Add 1 as we index over 0 and we need to catch up
                    if idea in values and Group_Ideas[i + 1] in values:
                        has_found_policy = True
                        table_row.append(key)

                if not has_found_policy:
                    table_row.append("missing")

            i += 1

        Idea_Table.append(table_row)

    print(make_markdown_table(Idea_Table))
