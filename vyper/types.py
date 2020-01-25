import ast as py_ast

from . import ast as vy_ast


class TypeChecker(py_ast.NodeVisitor):
    pass


def create_context(var_list):
    context = dict()  # Store our variables as we go along (Depth-first search so it's safe)
    for var in var_list:
        assert var.type is not None, "Can't have null types for storage!"
        context[var.name] = var.type
    return context


#NOTE: Don't make this available because it's a specific algorithm
class _TypeAnnotator(py_ast.NodeTransformer):
    context = dict()  # Store our variables as we go along (Depth-first search so it's safe)

    def visit_Module(self, node):
        # Global context is available throughout search
        context = create_context(node.variables)
        self.context.update(context)
        # TODO: Add environment variables
        for method in node.methods:
            self.visit(method)
        return node

    def visit_Method(self, node):
        context = create_context(node.parameters)
        self.context.update(context)
        for stmt in node.body:
            self.visit(stmt)
        # Delete context after visiting all statements
        self.context = {k: v for k, v in self.context.items() if k not in context}
        return node

    def visit_Attribute(self, node):
        import pdb; pdb.set_trace()
        if node.var.type is None:
            if node.var.name is not 'self':
                node.var = self.visit(node.var)
            else:
                node.var.type = 'self'
        node.type = self.context.get[node.var.name][node.property]
        return node

    def visit_Var(self, node):
        import pdb; pdb.set_trace()
        if node.type is None:
            assert node.name in self.context.keys(), f"Cannot find '{node.name}' in context!"
            node.type = self.context[node.name]
        return node

    # TODO: For and If statments


def type_check(ast: vy_ast.Ast) -> vy_ast.Ast:
    ast = _TypeAnnotator().visit(ast)
    TypeChecker().visit(ast)  # Check for type continuity
    return ast
