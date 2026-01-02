from typing import Any
from src.interpreter import TreeProcessor
from src.parser import AST, Num, BinOp


class RPN(TreeProcessor):
    def visit(self, node: AST) -> str:
        if isinstance(node, Num):
            return str(node.value)
        if not isinstance(node, BinOp):
            raise NotImplementedError()
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"{left} {right} {node.op.value}"


class LISP(TreeProcessor):
    def visit(self, node: AST) -> Any:
        if isinstance(node, Num):
            return str(node.value)
        if not isinstance(node, BinOp):
            raise NotImplementedError()
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"({node.op.value} {left} {right})"
