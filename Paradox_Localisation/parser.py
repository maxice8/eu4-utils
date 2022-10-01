from sly import Parser

from Paradox_Localisation.lexer import LocalisationLexer


# TODO: make so this returns a single shared dict with different keys,
# in the meantime we will have to deal with compressing it ourselves.
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
