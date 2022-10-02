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

from .lexer import SimpleCWLexer
from .parser import SimpleCWParser

__all__ = (
    "SimpleCWLexer",
    "SimpleCWParser",
)
