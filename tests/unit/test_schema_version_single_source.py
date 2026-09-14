import ast
import inspect

from app.architecture_intelligence import service as service_module
from app.architecture_intelligence.contracts import ARCHITECTURE_SCHEMA_VERSION


def test_service_answer_constructors_use_shared_schema_version():
    tree = ast.parse(inspect.getsource(service_module))
    values = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Subscript):
            continue
        if not isinstance(node.func.value, ast.Name) or node.func.value.id != "ArchitectureAnswer":
            continue
        values.extend(keyword.value for keyword in node.keywords if keyword.arg == "schema_version")

    assert len(values) == 6
    assert all(
        isinstance(value, ast.Name) and value.id == "ARCHITECTURE_SCHEMA_VERSION"
        for value in values
    )
    assert ARCHITECTURE_SCHEMA_VERSION == "0.4"
