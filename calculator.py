"""Bounded arithmetic calculator: no eval, assignments, or Python access."""
import ast
import math
import operator


def calculate(expression, variables):
    if not expression.strip() or len(expression) > 1500:
        raise ValueError('Enter an expression of at most 1,500 characters.')
    try:
        tree = ast.parse(expression, mode='eval')
        if sum(1 for _ in ast.walk(tree)) > 300:
            raise ValueError('This expression is too long.')

        def visit(node):
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                result = float(node.value)
            elif isinstance(node, ast.Name) and node.id in variables:
                result = float(variables[node.id])
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                result = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
            elif isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
                operations = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul, ast.Div:operator.truediv}
                result = operations[type(node.op)](visit(node.left), visit(node.right))
            elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id == 'exp' and len(node.args) == 1 and not node.keywords):
                result = math.exp(visit(node.args[0]))
            else:
                raise ValueError('Use numbers, the listed symbols, +, − (typed as -), *, /, parentheses, and exp(...).')
            if not math.isfinite(result) or abs(result) > 1e12:
                raise ValueError('The result is outside the calculator range.')
            return result

        return visit(tree.body)
    except (SyntaxError, ZeroDivisionError, OverflowError, TypeError, RecursionError) as exc:
        raise ValueError('Check the arithmetic, parentheses and denominators.') from exc
