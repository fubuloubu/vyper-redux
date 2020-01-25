import ast as py_ast
import inspect
import sys
from typing import (
    Dict,
    List,
    Tuple,
    Type,
    Union,
)

import lark

class Ast(py_ast.AST):
    _fields = ()


class Module(Ast):
    _fields = ('methods',)

    def __init__(self, args):
        self.methods = filter_ast(args, Method)


class Method(Ast):
    _fields = (
        'decorators',
        'name',
        'body',
    )

    def __init__(self, args):
        decorators_node, children = split(args, "decorators")
        self.decorators = decorators_node.children
        
        method_type, children = split(children, "method_type")
        method_type = convert_to_dict(method_type)
        self.name = method_type['NAME']

        body, children = split(children, "body")
        self.body = body.children

        assert len(children) == 0, f"Did not save everything: {children}"


class Decorator(Ast):
    _fields = (
        'type',
    )

    def __init__(self, args):
        assert args[0].type == 'DECORATOR_NAME'
        self.type = args[0].value


class Statement(Ast):
    pass


class Pass_Stmt(Statement):
    def __init__(self, arg):
        pass  # NOTE: Check later for only statement in body


def filter_ast(nodes: List[Ast], ast_type: Type[Ast], exclusive=False) -> List[Ast]:
    return [n for n in nodes if isinstance(n, ast_type) ^ exclusive]


def split(nodes: List[lark.Tree], rule_type: str) -> Tuple[lark.Tree, List[lark.Tree]]:
    selected = [n for n in nodes if n.data == rule_type]
    assert len(selected) == 1, "Cannot cherry pick more than 1 node."
    others = [n for n in nodes if n.data != rule_type]
    return selected[0], others


def convert_to_dict(node: Union[lark.Tree, lark.Token]) -> Dict:
    obj = dict()
    for n in node.children:
        if isinstance(n, lark.Token):
            obj[n.type] = n.value
        elif isinstance(n, lark.Tree):
            obj[n.data] = convert_to_dict(n)
        else:
            raise ValueError("Cannot convert {n}.")
    return obj


def _get_ast_classes():
    ast_classes = dict()
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, Ast):
            ast_classes[name] = obj
    return ast_classes


AST_CLASSES = _get_ast_classes()


class AstConverter(lark.Transformer):
    def __init__(self, *args, **kwargs):
        for name, ast_class in _get_ast_classes().items():
            setattr(self, name.lower(), ast_class)
        super().__init__(*args, **kwargs)


class _CheckLarkConversionFailures(py_ast.NodeVisitor):
    def visit(self, node):
        node_class = node.__class__.__name__
        for member_name in node._fields:
            member = getattr(node, member_name)
            if isinstance(member, (lark.Tree, lark.Token)):
                raise ValueError(
                        f"Could not convert {member_name} in {node_class}: {member}"
                    )
            if isinstance(member, list):
                for item in member:
                    if isinstance(item, (lark.Tree, lark.Token)):
                        raise ValueError(
                                f"Could not convert {member_name} in {node_class}: {item}"
                            )
        super().visit(node)


def ast_parse(parse_tree: lark.Tree) -> Ast:
    ast = AstConverter().transform(parse_tree)
    _CheckLarkConversionFailures().visit(ast)
    return ast
