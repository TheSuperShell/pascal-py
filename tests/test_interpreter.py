from hypothesis import given, strategies as st
import pytest
from src.interpreter import DefaultVisitor, Interpreter
from src.lexer import Lexer
from src.parser import Parser
from src.semantic_analyzer import SemanticError


OPS = ["+", "-", "*", "DIV", "/"]


@given(
    st.lists(
        st.tuples(
            st.integers(),
            st.integers(min_value=0, max_value=4),
            st.integers(min_value=1, max_value=3),
        ),
        min_size=1,
    )
)
def test_intepreter_math(int_op: list[tuple[int, int, int]]):
    opened_p = 0
    inp = []
    if int_op[0][2] == 1:
        inp = ["("]
        opened_p = 1
    inp.append(str(int_op[0][0]))
    for i in range(0, len(int_op) - 1):
        if opened_p > 0 and int_op[i + 1][2] == 3:
            inp.append(")")
            opened_p -= 1
        inp.append(f" {OPS[int_op[i][1]]} ")
        if int_op[i + 1][2] == 2:
            inp.append("(")
            opened_p += 1
        inp.append(str(int_op[i + 1][0]))
    for _ in range(opened_p):
        inp.append(")")
    code = "".join(inp)
    pascal_code = f"PROGRAM name; BEGIN a:={code}; END."
    lexer = Lexer(pascal_code)
    parser = Parser(lexer)
    visitor = DefaultVisitor()
    interpreter = Interpreter(parser, visitor)
    try:
        result = eval(code.replace("DIV", "//"))
    except ZeroDivisionError:
        with pytest.raises(ZeroDivisionError):
            interpreter.process()
        return
    interpreter.process()
    assert result == visitor.call_stack.get_popped_records()[0]["a"]


def test_intepreter_assign():
    lexer = Lexer("PROGRAM name; BEGIN a:= 5; b:=10; c:= a + b; END.")
    parser = Parser(lexer)
    visitor = DefaultVisitor()
    interpreter = Interpreter(parser, visitor)
    interpreter.process()
    assert visitor.call_stack.get_popped_records()[0]["a"] == 5
    assert visitor.call_stack.get_popped_records()[0]["b"] == 10
    assert visitor.call_stack.get_popped_records()[0]["c"] == 15


def test_intepreter_assign_error():
    lexer = Lexer("PROGRAM name; BEGIN a:= 5; c:= a + k; END.")
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    with pytest.raises(SemanticError):
        interpreter.process()
