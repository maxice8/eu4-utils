from typing import Any
from Paradox_Localisation.lexer import LocalisationLexer
from Paradox_Localisation.parser import LocalisationParser


def generate_localisation(
    dir: str, extra_dirs: str | list[str] | None = None
) -> dict[str, dict[str, Any]]:
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

    # Get all the modding ones after as they are the ones that will
    # end up composing the final dictionary, I really should make the
    # parser work by having a single dictionary.
    for file in os.listdir(dir + "/localisation"):
        if not file.endswith("l_english.yml"):
            continue
        # open with utf-8-sig because of the Byte-Order-Mark required
        # in localisation files
        with open(f"{dir}/localisation/{file}", "r", encoding="utf-8-sig") as fd:
            wfd.write(fd.read())
            wfd.write("\n")

        # Don't bother checking if in set, this is the first time
        files_seen.add(file)

    # Get all the base games ones if given to us
    if extra_dirs is not None:
        if type(extra_dirs) is str:
            # Redeclare as a list
            extra_dirs = [extra_dirs]
        # For some reason args.base is passed as a [list] but it only
        # receives a single argument
        for dire in reversed(extra_dirs):
            for file in os.listdir(dire + "/localisation"):
                if not file.endswith("l_english.yml") or file in files_seen:
                    continue
                with open(
                    f"{dire}/localisation/{file}", "r", encoding="utf-8-sig"
                ) as fd:
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
