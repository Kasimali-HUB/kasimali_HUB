import ast
from pathlib import Path

LEGISLATION_DIR = Path(__file__).resolve().parent.parent / "app" / "legislation"

# Modules that can hold or touch real employee/client data. The legislation
# package should never import any of these, directly or indirectly - that's
# what makes the AI/data boundary a property of the code, not just a rule
# someone has to remember to follow.
FORBIDDEN_IMPORT_PREFIXES = ("app.exceptions", "app.db")


def _imported_modules(source_file: Path) -> set[str]:
    tree = ast.parse(source_file.read_text())
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_legislation_module_never_imports_pii_bearing_modules():
    violations = []
    for py_file in LEGISLATION_DIR.rglob("*.py"):
        for module in _imported_modules(py_file):
            if module.startswith(FORBIDDEN_IMPORT_PREFIXES):
                violations.append(f"{py_file.name} imports {module}")

    assert not violations, (
        "Legislation module must never import PII-bearing modules: " + ", ".join(violations)
    )
