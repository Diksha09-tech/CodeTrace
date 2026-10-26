
import ast
import builtins


def explain_error(message):
    if "was never closed" in message:
        return "You opened a bracket or parenthesis but did not close it."
    elif "unterminated string literal" in message:
        return "Your string is missing a closing quotation mark."
    elif "invalid syntax" in message:
        return "Check your brackets, quotes, colons, and Python statements."
    elif "division by zero" in message:
        return "You cannot divide a number by zero."
    else:
        return "Review the code around the reported issue."


class VariableChecker(ast.NodeVisitor):
    def __init__(self):
        self.scopes = [set(dir(builtins))]
        self.errors = []

    def visit_FunctionDef(self, node):
        self.scopes[-1].add(node.name)

        local_names = {
            arg.arg
            for arg in (
                node.args.posonlyargs
                + node.args.args
                + node.args.kwonlyargs
            )
        }

        if node.args.vararg:
            local_names.add(node.args.vararg.arg)

        if node.args.kwarg:
            local_names.add(node.args.kwarg.arg)

        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(
                child.ctx, ast.Store
            ):
                local_names.add(child.id)

        self.scopes.append(set(dir(builtins)) | local_names)

        for statement in node.body:
            self.visit(statement)

        self.scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        names = {arg.arg for arg in node.args.args}
        self.scopes.append(set(dir(builtins)) | names)
        self.visit(node.body)
        self.scopes.pop()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.scopes[-1].add(node.id)

        elif isinstance(node.ctx, ast.Load):
            if not any(node.id in scope for scope in self.scopes):
                self.errors.append(
                    (node.id, node.lineno)
                )


def analyze_code(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return (
            "Error type: SyntaxError\n"
            f"Line: {error.lineno}\n"
            f"Details: {error.msg}\n"
            f"Explanation: {explain_error(error.msg)}"
        )

    # Check for obvious division by zero
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Div, ast.FloorDiv, ast.Mod)
        ):
            divisor = node.right

            if (
                isinstance(divisor, ast.Constant)
                and isinstance(divisor.value, (int, float))
                and not isinstance(divisor.value, bool)
                and divisor.value == 0
            ):
                return (
                    "Potential error: Division by zero\n"
                    f"Line: {node.lineno}\n"
                    "Explanation: You cannot divide by zero.\n"
                    "Suggestion: Check the divisor before performing the operation."
                )

    # Check obvious list index errors
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.List)
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, int)
            and not isinstance(node.slice.value, bool)
        ):
            index = node.slice.value
            length = len(node.value.elts)

            if index >= length or index < -length:
                return (
                    "Potential error: List index out of range\n"
                    f"Line: {node.lineno}\n"
                    "Suggestion: Check the list length and index."
                )

    # Check likely undefined variables
    checker = VariableChecker()

    for statement in tree.body:
        checker.visit(statement)

    if checker.errors:
        name, line = checker.errors[0]
        return (
            "Potential error: Undefined variable\n"
            f"Variable: {name}\n"
            f"Line: {line}\n"
            "Suggestion: Define the variable before using it."
        )

    return (
        "Analysis completed successfully!\n"
        "No known issues detected by the current checks.\n"
        "Note: This basic static analyzer cannot detect every Python error."
    )
