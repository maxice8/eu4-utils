from sly import Parser

from Simple_Clausewitz.lexer import SimpleCWLexer


class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SimpleCWParser(Parser):
    # Need
    tokens = SimpleCWLexer.tokens

    # Raise an error
    def error(self, p):
        if p:
            raise ParseError(
                (
                    "Token parse error: token=%s type=%s line=%s index=%s"
                    % (p.value, p.type, p.lineno, p.index)
                )
            )
        if not p:
            raise ParseError("Syntax error at EOF")

    @_("{ pair }")
    def file(self, p):
        return p.pair

    @_('"{" { pair } "}"')
    def map(self, p):
        return p.pair

    @_("field SPECIFIER value")
    def pair(self, p):
        return p[0], p[2]

    @_('"{" { value } "}"')
    def array(self, p):
        return p.value

    @_("DATE")
    def value(self, p):
        return p[0]

    @_("BOOL")
    def value(self, p):
        return p[0]

    @_("INTEGER")
    def value(self, p):
        return p[0]

    @_("INTEGER")
    def field(self, p):
        return p[0]

    @_("FLOAT")
    def value(self, p):
        return p[0]

    @_("STRING")
    def value(self, p):
        return p[0]

    @_("STRING")
    def field(self, p):
        return p[0]

    @_("map")
    def value(self, p):
        return p.map

    @_("array")
    def value(self, p):
        return p.array
