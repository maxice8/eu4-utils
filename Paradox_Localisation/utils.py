from typing import Any
from Paradox_Localisation.lexer import LocalisationLexer
from Paradox_Localisation.parser import LocalisationParser


def generate_localisation(
    dirs: list[str], language: str = "english"
) -> dict[str, dict[str, Any]]:
    """generate localisation from list of directories.

    Args:
        dirs (list[str]): list of paths to directories where we get load all the localisation files.
        language (str, optional): which language do we get our localisation for. Defaults to "english".

    Returns:
        dict[str, dict[str, Any]]: a dictionary of dictionaries keyed by the localisation key and holding the value of the localisation and its version.
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
            if not file.endswith(f"l_{language}.yml") or file in files_seen:
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
