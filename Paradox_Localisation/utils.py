from typing import Any
from Paradox_Localisation.lexer import LocalisationLexer
from Paradox_Localisation.parser import LocalisationParser


def generate_localisation(dir: str, base: str = None) -> dict[str, dict[str, Any]]:
    """Generate a dictionary of dictionary representing localisation keys

    Args:
        dir (str): directory of the mod to get localisation
        base (str, optional): base game to get localisation as
        a backup. Defaults to None.

    Returns:
        dict[str, dict[str, Any]]: A dictionary of dictionaries
        representing localisation keys
    """

    import io
    import os

    localisation: dict[str, dict[str, Any]] = dict()

    # Will hold ALL the files that we are going to parse
    wfd = io.StringIO()

    # Get all the base games ones if given to us
    if base is not None:
        # For some reason args.base is passed as a [list] but it only
        # receives a single argument
        for file in os.listdir(base[0] + "/localisation"):
            if not file.endswith("l_english.yml"):
                continue
            with open(
                f"{base[0]}/localisation/{file}", "r", encoding="utf-8-sig"
            ) as fd:
                wfd.write((fd.read()))
                wfd.write("\n")

    # Get all the modding ones after as they are the ones that will
    # end up composing the final dictionary, I really should make the
    # parser work by having a single dictionary.
    for file in os.listdir(dir + "/localisation"):
        if not file.endswith("l_english.yml"):
            continue
        with open(f"{dir}/localisation/{file}", "r", encoding="utf-8-sig") as fd:
            wfd.write(fd.read())
            wfd.write("\n")

    stream = wfd.getvalue()

    # Lex and Parse
    lexer = LocalisationLexer()
    parser = LocalisationParser()
    result = parser.parse(lexer.tokenize(stream))

    # Create our new dictionary
    for res in result:
        if type(res) is not dict:
            continue

        localisation[res["key"]] = {"value": res["value"], "version": res["version"]}

    return localisation
