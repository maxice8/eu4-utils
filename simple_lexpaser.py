# IdeasLexer

from sly import Lexer, Parser

class SimpleClausewitzLexer(Lexer):
    tokens = {
        STATEMENT,
        INTEGER,
        FLOAT,
        BOOL
    }

    literals = { '{', '=', '}' }
    ignore = ' \t'

    @_(r"(yes|no)")
    def BOOL(self, t):
        t.value = bool(t.value)
        return t

    @_(r"\d+\.\d*")
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INTEGER(self, t):
        t.value = int(t.value)
        return t

    # Inside a "double-quoted string" we must take space into
    # account too
    @_(r'[\w_\.-]+', r'".*?"')
    def STATEMENT(self, t):
        # Strip double-quotes from a quoted string with no
        # spaces
        if '\"' in t.value:
            if ' ' not in t.value:
                t.value = t.value.strip('\"')
        return t

    
    # Line number tracking
    @_(r'\n')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    # Ignore comments
    ignore_comment = r'\#.*'

class SimpleClausewitzParser(Parser):
    # Need
    tokens = SimpleClausewitzLexer.tokens

    @_('{ assignment }')
    def expression(self, p):
        return p.assignment

    @_('statement "=" "{" { assignment } "}"')
    def assignment(self, p):
        return [p.statement] + p.assignment

    @_('statement "=" "{" { statement } "}"')
    def assignment(self, p):
        return [p.statement0] + p.statement1

    @_('statement "=" statement')
    def assignment(self, p):
        return p[0], p[2]

    @_('BOOL')
    def statement(self, p):
        return p[0]

    @_('INTEGER')
    def statement(self, p):
        return p[0]

    @_('FLOAT')
    def statement(self, p):
        return p[0]

    @_('STATEMENT')
    def statement(self, p):
        return p[0]

if __name__ == '__main__':
    lexer = SimpleClausewitzLexer()
    parser = SimpleClausewitzParser()

    cw_text = '''
    celestial_ideas = {
        category = DIP
        
        trigger = {
		    has_dlc = "Mandate of Heaven"
		    is_emperor_of_china = yes
    	}
    }
    globaldomination_ideas = {
	    category = DIP

	    trigger = {
		    has_global_flag = domination_ideas_enabled
		    OR = {
			    current_age = age_of_revolutions
			    current_age = age_of_imperialism
		    }
		    NOT = {
			    has_country_flag = ab_cant_pick_domination
		    }
            ship_durability = 0.5
	    }
    }
    south_pacific_area = {
	    1700 1701 1702 1703 1704 1705 1706 1707 1708 1709 1710 1711 1712 1716 1717  1718 1719 1730 1736 1737 1740 1741
    }
    '''

    """
    cw_text = '''
    south_pacific_area = {
	    1700 1701 1702 1703 1704 1705 1706 1707 1708 1709 1710 1711 1712 1716 1717  1718 1719 1730 1736 1737 1740 1741
    }
    '''
    """

    lexed = lexer.tokenize(cw_text)
    result = parser.parse(lexed)
    for res in result:
        print(res)