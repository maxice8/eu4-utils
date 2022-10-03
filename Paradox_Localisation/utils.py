from typing import Any
from Paradox_Localisation.lexer import LocalisationLexer
from Paradox_Localisation.parser import LocalisationParser


def generate_localisation(dirs: list[str]) -> dict[str, dict[str, Any]]:
    """Generate a dictionary of dictionary representing localisation keys

    Args:
        dir (str): directory of the mod to get localisation
        base (str, list[str], optional): collection of directories to load localisation from, directories are read in reverse given order so you can pass the base game first then any mods in the loading order. Defaults to None.

    Returns:
        dict[str, dict[str, Any]]: A dictionary of dictionaries
        representing localisation keys
    """

    import io
    import os

    localisation: dict[str, dict[str, Any]] = dict()

    # Set of files that we have seen already, they are added as
    # we read the files
    files_seen: set[str] = set()

    # Will hold ALL the files that we are going to parse
    wfd = io.StringIO()

    # Get all the base games ones if given to us
    for dir in reversed(dirs):
        for file in os.listdir(dir + "/localisation"):
            if not file.endswith("l_english.yml") or file in files_seen:
                continue
            with open(f"{dir}/localisation/{file}", "r", encoding="utf-8-sig") as fd:
                wfd.write((fd.read()))
                wfd.write("\n")

            # Say we have seen the file
            files_seen.add(file)

    stream = wfd.getvalue()

    # Lex and Parse
    lexer = LocalisationLexer()
    parser = LocalisationParser()
    result = parser.parse(lexer.tokenize(stream))

    # Create our new dictionary
    for res in result:
        # Do not add the key if it already exists, this allows us to
        # override files by first loading the mod, then loading each
        # game in descending order
        if type(res) is not dict or res["key"] in localisation:
            continue

        localisation[res["key"]] = {
            "value": res["value"],
            "version": res["version"],
        }

    return localisation
