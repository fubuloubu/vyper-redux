import ast as py_ast
import inspect
import sys
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Type,
    Union,
)

import lark
import stringcase

class Ast(py_ast.AST):
    _fields = ()


class Module(Ast):
    _fields = ('methods',)

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        self.methods, children = split_ast(children, Method)
        self.variables, children = split_ast(children, Variable)

        assert len(children) == 0, f"Did not save everything: {children}"


class Method(Ast):
    _fields = (
        'decorators',
        'name',
        'parameters',
        'body',
    )

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        decorators_node, children = split_tree(children, "decorators")
        assert len(decorators_node) <= 1, "Should not have more than 1 set of decorators"
        self.decorators = decorators_node[0].children
        
        method_type, children = split_tree(children, "method_type")
        assert len(method_type) == 1, "Should not have more than 1 method_type"
        method_type = convert_to_dict(method_type[0].children)
        self.name = method_type['NAME']

        self.parameters = method_type.get('parameters', None)

        body, children = split_tree(children, "body")
        assert len(body) == 1, "Should not have more than 1 body"
        self.body = body[0].children

        assert len(children) == 0, f"Did not save everything: {children}"



class Decorator(Ast):
    _fields = (
        'type',
    )

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        assert len(children) == 1
        assert children[0].type == 'DECORATOR_NAME'
        self.type = children[0].value


class Statement(Ast):
    pass


class PassStmt(Statement):
    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        pass  # NOTE: Check later for only statement in body


class ExprStmt(Statement):
    _fields = (
        'assignment',
        'expression',
    )

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        assert len(children) == 2
        self.assignment = children[0]
        self.expression = children[1]


class Var(Ast):
    _fields = (
        'name',
        'type',
    )

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        properties = convert_to_dict(children)
        self.name = properties['NAME']
        self.type = properties.get('TYPE', None)  # NOTE: Do not know type yet if none


class Variable(Ast):
    _fields = (
        'name',
        'type',
        'public',
    )

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        properties = convert_to_dict(children)
        if 'with_getter' in properties.keys():
            self.public = True
            properties = properties['with_getter']
        else:
            self.public = False
        self.name = properties['NAME']
        self.type = get_type(properties)


class Parameter(Variable):
    pass

class Attribute(Var):
    _fields = (
        'var',
        'property',
    )

    def __init__(self, children: List[Union[lark.Tree, lark.Token]]):
        assert len(children) == 2
        self.var = children[0]
        properties = convert_to_dict(children[1])
        self.property = properties['NAME']


def split_ast(
    nodes: List[Ast],
    ast_type: Type[Ast],
) -> Tuple[List[Ast], List[Ast]]:
    selected = [n for n in nodes if isinstance(n, ast_type)]
    others = [n for n in nodes if not isinstance(n, ast_type)]
    return selected, others


def split_tree(
    nodes: List[lark.Tree],
    rule_type: str,
) -> Tuple[List[lark.Tree], List[lark.Tree]]:
    selected = [n for n in nodes if n.data == rule_type]
    others = [n for n in nodes if n.data != rule_type]
    return selected, others


def convert_to_dict(
        node: Union[List[Union[lark.Tree, lark.Token, Ast]], Union[lark.Tree, lark.Token, Ast]],
) -> Dict:
    if isinstance(node, lark.Token):
        return {node.type: node.value}
    elif isinstance(node, lark.Tree):
        return {node.data: convert_to_dict(node.children)}
    elif isinstance(node, list):
        obj = list()
        for n in node:
            attr = convert_to_dict(n)
            obj.append(attr)
        minified_obj = dict()
        for item in obj:
            if isinstance(item, dict) and all([k not in minified_obj.keys() for k in item.keys()]):
                minified_obj.update(item)
            else:
                return obj  # Give up an abort
        return minified_obj
    elif isinstance(node, Ast):
        return node
    else:
        raise ValueError(f"Cannot convert {node}.")


def get_type(properties: Dict[str, Any]) -> str:
    if 'storage' in properties.keys():
        return get_type(properties['storage'])
    if 'abi_type' in properties.keys():
        return get_type(properties['abi_type'])
    if 'memory' in properties.keys():
        return get_type(properties['memory'])
    if 'BASIC_TYPE' in properties.keys():
        return properties['BASIC_TYPE']
    raise ValueError(f"Could not process {properties}.")


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
            # NOTE: Convention is for classnames to be CamalCase,
            #       but Lark rules are snake_case
            setattr(self, stringcase.snakecase(name), ast_class)
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
