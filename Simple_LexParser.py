# Simple_LexParser

"""
Taken from: https://github.com/QAston/clausewitz-antlr-grammar
grammar CLAUSEWITZ;

file
   : (pair)*
   ;

map
   : '{' (pair)* '}'
   ;

pair
   : STRING SPECIFIER value
   ;

SPECIFIER
    : '=' | '<>' | '>' | '<' | '<=' | '>=' ;

array
   : '{' value+ '}'
   ;

value
   : INT
   | PCT
   | REAL
   | DATE
   | STRING
   | map
   | array
   ;

INT
   : '-'?[0-9]+;

PCT
   : '-'?[0-9]+'%';

REAL
   : '-'?[0-9]+'.'[0-9]+;

DATE
   : [0-9]+'.'[0-9]+'.'[0-9]+;

STRING
   : '"'(~["])*'"'
   | [A-Za-z][A-Za-z_0-9.%-]*
   ;

WS
   : [ \t\n\r] + -> skip
   ;

LINE_COMMENT
    : '#'~[\r\n]* -> channel(HIDDEN)
    ;
"""

from sly import Lexer, Parser


class SimpleClausewitzLexer(Lexer):
    tokens = {STRING, INTEGER, FLOAT, BOOL, DATE, SPECIFIER}

    literals = {"{", "}"}
    ignore = " \t"

    SPECIFIER = r"="

    # Very important to use Word Boundary when grabbing these
    @_(r"\b(yes|no)\b")
    def BOOL(self, t):
        t.value = bool(t.value)
        return t

    DATE = r"\-?\d+\.\d+\.\d+"

    @_(r"\-?\d+\.\d+")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r"\-?\d+")
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    # STRING is just a SYMBOL but it can contain whitespace
    # due to being enclosed in double quotes
    @_(r'"[^"]*"', r"[A-Za-z][A-Za-z_0-9.%-:]*")
    def STRING(self, t):
        # Strip double-quotes from a quoted string with no
        # spaces
        if '"' in t.value:
            if " " not in t.value:
                t.value = t.value.strip('"')
        return t

    # Line number tracking
    @_(r"\n")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    # Ignore comments
    ignore_comment = r"\#.*"

    def error(self, t):
        print("Illegal Character '%s'" % t.value[0])
        self.index += 1


class SimpleClausewitzParser(Parser):
    # Need
    tokens = SimpleClausewitzLexer.tokens

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
