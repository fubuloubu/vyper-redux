from .ast import (
    ast_parse,
)
from .grammar import (
    grammar,
)

def compile_code(src: str):
    tree = grammar.parse(src + '\n')  # Python newline bug
    ast = ast_parse(tree)
    import pdb; pdb.set_trace()
