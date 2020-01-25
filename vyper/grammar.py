from lark import (
    Lark as _Lark,
)
from lark.indenter import (
    Indenter as _Indenter,
)


class _PythonIndenter(_Indenter):
    NL_type = '_NEWLINE'
    OPEN_PAREN_types = ['LPAR', 'LSQB', 'LBRACE']
    CLOSE_PAREN_types = ['RPAR', 'RSQB', 'RBRACE']
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4


grammar = _Lark.open(
    'vyper/grammar.lark',
    parser='lalr',
    start='module',
    postlex=_PythonIndenter()
)
