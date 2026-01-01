from hypothesis import given, strategies as st
import pytest
from src.interpreter import Interpreter
from src.lexer import Lexer


OPS = ["+", "-", "*", "/"]


@given(
    st.lists(
        st.tuples(
            st.integers(min_value=1),
            st.integers(min_value=0, max_value=3),
            st.integers(min_value=1, max_value=3),
        ),
        min_size=2,
    )
)
def test_intepreter_math(int_op: list[tuple[int, int, int]]):
    inp = [str(int_op[0][0])]
    opened_p = 0
    for i in range(0, len(int_op) - 1):
        if opened_p > 0 and int_op[i][2] == 3:
            inp.append(")")
            opened_p -= 1
        inp.append(OPS[int_op[i][1]])
        if int_op[i][2] == 2:
            inp.append("(")
            opened_p += 1
        inp.append(str(int_op[i + 1][0]))
    for _ in range(opened_p):
        inp.append(")")
    code = "".join(inp)
    lexer = Lexer(code)
    interpreter = Interpreter(lexer)
    print(code)
    try:
        result = eval(code.replace("/", "//"))
    except ZeroDivisionError:
        with pytest.raises(ZeroDivisionError):
            interpreter.expr()
        return
    assert result == interpreter.expr()
