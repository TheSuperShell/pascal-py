from hypothesis import HealthCheck, given, settings, strategies as st
import pytest
from interpreter.interpreter import Interpreter
from parser.lexer import Lexer
from parser import Parser
from interpreter.semantic_analyzer import SemanticError, SymbolTableVisitor


OPS = ["+", "-", "*", "DIV", "/"]


@given(
    int_op=st.lists(
        st.tuples(
            st.integers(),
            st.integers(min_value=0, max_value=4),
            st.integers(min_value=1, max_value=3),
        ),
        min_size=1,
    )
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_intepreter_math(int_op: list[tuple[int, int, int]], logger):
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
    tree = parser.parse()
    interpreter = Interpreter(logger)
    try:
        result = eval(code.replace("DIV", "//"))
    except ZeroDivisionError:
        with pytest.raises(ZeroDivisionError):
            interpreter.interpret(tree)
        return
    interpreter.interpret(tree)
    assert result == interpreter.call_stack.get_popped_records()[0]["a"]


def test_intepreter_assign(logger):
    lexer = Lexer("PROGRAM name; BEGIN a:= 5; b:=10; c:= a + b; END.")
    parser = Parser(lexer)
    interpreter = Interpreter(logger)
    interpreter.interpret(parser.parse())
    assert interpreter.call_stack.get_popped_records()[0]["a"] == 5
    assert interpreter.call_stack.get_popped_records()[0]["b"] == 10
    assert interpreter.call_stack.get_popped_records()[0]["c"] == 15


def test_intepreter_assign_error(logger):
    lexer = Lexer("PROGRAM name; BEGIN a:= 5; c:= a + k; END.")
    parser = Parser(lexer)
    interpreter = SymbolTableVisitor.new(logger)
    with pytest.raises(SemanticError):
        interpreter.analyze(parser.parse())
