from .ast import (
    ast_parse,
)
from .grammar import (
    grammar,
)
from .types import (
    type_check,
)

def compile_code(src: str):
    tree = grammar.parse(src + '\n')  # Python newline bug
    ast = ast_parse(tree)
    typed_ast = type_check(ast)
    import pdb; pdb.set_trace()
