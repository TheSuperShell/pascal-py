from hypothesis import given, strategies as st
from src.interpreter import Interpreter
from src.lexer import Lexer


OPS = ["+", "-", "*", "/"]


@given(
    st.lists(
        st.tuples(
            st.integers(min_value=1),
            st.integers(min_value=1, max_value=3),
        ),
        min_size=2,
    )
)
def test_intepreter_math(int_op: list[tuple[int, int]]):
    inp = [str(int_op[0][0])]
    for i in range(0, len(int_op) - 1):
        inp.append(OPS[int_op[i][1]])
        inp.append(str(int_op[i + 1][0]))
    code = "".join(inp)
    lexer = Lexer(code)
    interpreter = Interpreter(lexer)
    assert eval(code.replace("/", "//")) == interpreter.expr()
