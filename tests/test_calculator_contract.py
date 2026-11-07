"""Source and metadata checks for the calculator Space.

These tests do not import Streamlit, start a server, or contact Hugging Face.
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SPACES_FRONTMATTER = """\
title: Calculator_app
emoji: 📊
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.10.0
app_file: app.py
pinned: false\
"""


def _app_tree() -> ast.AST:
    return ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))


def _slider_args(tree: ast.AST) -> list[tuple[object, ...]]:
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "slider"
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
        ):
            continue
        found.append(tuple(ast.literal_eval(arg) for arg in node.args))
    return found


def test_app_parses_and_imports_declared_dependencies():
    tree = _app_tree()
    imported = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert {"numpy", "streamlit"} <= imported


def test_sliders_keep_their_ranges_and_the_result_is_their_sum():
    tree = _app_tree()
    assert _slider_args(tree) == [
        ("Select a range of values for first argument", 300.0, 500.0),
        ("Select a range of values for second argument", 180.0, 200.0),
    ]

    addition = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "addition"
            for target in node.targets
        ):
            addition = node.value
    assert isinstance(addition, ast.BinOp)
    assert isinstance(addition.op, ast.Add)
    assert isinstance(addition.left, ast.Name) and addition.left.id == "value1"
    assert isinstance(addition.right, ast.Name) and addition.right.id == "value2"

    writes_sum = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "write"
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
        ):
            continue
        writes_sum = any(
            isinstance(arg, ast.Name) and arg.id == "addition" for arg in node.args
        )
    assert writes_sum


def test_spaces_frontmatter_is_unchanged():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.startswith("---\n")
    end = readme.index("\n---\n", 4)
    assert readme[4:end] == SPACES_FRONTMATTER


def test_runtime_dependencies_are_pinned_to_the_space():
    lines = []
    for raw in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    assert lines == ["numpy==1.23.5", "streamlit==1.10.0", "altair==4.2.2"]


def test_sync_workflow_stays_on_main_and_keeps_the_existing_push():
    workflow = (ROOT / ".github/workflows/main.yml").read_text(encoding="utf-8")
    trigger, _, jobs = workflow.partition("jobs:")
    assert "pull_request" not in trigger
    assert "branches: [main]" in trigger
    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "persist-credentials: false" in workflow
    assert (
        "github.repository == 'BhaveshWadibhasme/HuggingFaceSpaces' "
        "&& github.ref == 'refs/heads/main' "
        "&& github.event_name != 'pull_request'"
    ) in workflow
    assert (
        'git push --force "https://Bhavesh302:${HF_TOKEN}@huggingface.co/spaces/Bhavesh302/Calculator_app" main'
        in workflow
    )
    assert "--force" in workflow
    assert "secrets.HF_TOKEN" in workflow
    assert "actions/checkout@v2" not in workflow
    assert jobs
