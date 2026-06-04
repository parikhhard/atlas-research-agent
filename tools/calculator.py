"""
Calculator tool. Evaluates math expressions safely.

Note: we use a restricted eval here for simplicity. In production you'd use
a real math parser like sympy or a dedicated expression parser.
"""

import ast
import operator


CALCULATOR_DEFINITION = {
    "name": "calculate",
    "description": (
        "Evaluate a mathematical expression. "
        "Supports +, -, *, /, **, parentheses, and decimal numbers. "
        "Pass the full expression as a single string like '2 + 2 * 3' or '(150000 / 8500000) * 100'. "
        "Use this for multi digit arithmetic, percentages, ratios, and unit conversions. "
        "Do not call this for trivial math like '2+2' that you can do yourself."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The math expression to evaluate, as a string."
            }
        },
        "required": ["expression"]
    }
}


# Safe operator table — only allow these
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value}")
    if isinstance(node, ast.BinOp):
        op = OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
        return op(_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op = OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    raise ValueError(f"Unsupported node type: {type(node).__name__}")


def calculate(expression: str) -> str:
    """Safely evaluate a math expression and return the result as a string."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


if __name__ == "__main__":
    print(calculate("2 + 2 * 3"))           # 8
    print(calculate("(150000 / 8500000) * 100"))  # 1.7647...
    print(calculate("__import__('os').system('ls')"))  # blocked