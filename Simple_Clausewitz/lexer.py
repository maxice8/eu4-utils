from sly import Lexer


class SimpleCWLexer(Lexer):
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
