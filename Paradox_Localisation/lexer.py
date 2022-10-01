from sly import Lexer


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
