# Paradox_LocParser

from typing import Any
from sly import Lexer, Parser


class LocalisationLexer(Lexer):
    tokens = {
        KEY,
        STRING,
        INTEGER,
    }

    literals = {":"}
    # \ufeff is the Byte-Order-Mark that is at the start of every
    # localisation file, we choose to ignore it outright as it does
    # not affect anything
    ignore = " \t\ufeff"

    # Anything inside doule-quotes
    STRING = r'".*"'

    @_(r"\b[0-9]+\b")
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    # Something like localisation_key
    KEY = r"[A-Za-z0-9\_\-\.]+"

    # Line number tracking
    # Also account for \r\n from Windows
    @_(r"\n", r"\r\n")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    # Ignore comments
    ignore_comment = r"\#.*"

    def error(self, t):
        print("Line %d: Bad character %r" % (self.lineno, t.value[0]))
        self.index += 1


# TODO: make so this returns a single shared dict with different keys, in the meantime we will have to deal with compressing it ourselves.
class LocalisationParser(Parser):
    tokens = LocalisationLexer.tokens

    @_("{ key }")
    def expr(self, p):
        return p.key

    @_('field ":" version value')
    def key(self, p):
        dic = dict()
        dic["key"] = p.field
        dic["value"] = p.value
        dic["version"] = p.version
        return dic

    @_('field ":" value')
    def key(self, p):
        dic = dict()
        dic["key"] = p.field
        dic["value"] = p.value
        dic["version"] = 0
        return dic

    @_('field ":"')
    def key(self, p):
        return p[0]

    @_("INTEGER")
    def version(self, p):
        return p[0]

    @_("KEY")
    def field(self, p):
        return p[0]

    @_("STRING")
    def value(self, p):
        return p[0]


def generate_localisation(dir: str, base: str = None) -> dict[str, dict[str, Any]]:
    """Generate a dictionary of dictionary representing localisation keys

    Args:
        dir (str): directory of the mod to get localisation
        base (str, optional): base game to get localisation as a backup. Defaults to None.

    Returns:
        dict[str, dict[str, Any]]: A dictionary of dictionaries representing localisation keys
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
