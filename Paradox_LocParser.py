# Paradox_LocParser

from sly import Lexer, Parser


class ParadoxLocalisationLexer(Lexer):
    tokens = {
        KEY,
        STRING,
        INTEGER,
    }

    literals = {":"}
    ignore = " \t"

    @_(r"\-?\d+")
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    # Anything inside doule-quotes
    STRING = r'".*"'

    # Something like localisation_key
    KEY = r"[a-zA-Z][^ :]*"

    # Line number tracking
    @_(r"\n")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    # Ignore comments
    ignore_comment = r"\#.*"

    def error(self, t):
        print("Illegal Character '%s'" % t.value[0])
        self.index += 1


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
