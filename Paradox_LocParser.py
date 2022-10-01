# Paradox_LocParser

from sly import Lexer, Parser


class ParadoxLocalisationLexer(Lexer):
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
class ParadoxLocalisationParser(Parser):
    tokens = ParadoxLocalisationLexer.tokens

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
