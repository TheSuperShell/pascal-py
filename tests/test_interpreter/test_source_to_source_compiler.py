import pytest

from parser.lexer import Lexer
from parser.parser import Parser
from interpreter.source_to_source_compiler import S2SCompiler


@pytest.mark.parametrize(("expected_file_number",), [[i] for i in range(1, 4)])
def test_source_to_source_compiler(expected_file_number):
    with open(f"tests/test_examples/s2s_source_{expected_file_number}.pas") as f:
        source_code = f.read()
    with open(f"tests/test_examples/s2s_result_{expected_file_number}.pas") as f:
        expected_result = f.read()
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    s2s_compiler = S2SCompiler()
    result = s2s_compiler.build_output(parser.parse())
    assert expected_result.strip() == result.strip()
