"""Validate FR/EN/VI life-cycle form labels without importing Streamlit."""
import ast
from pathlib import Path
from string import Formatter


def _copy():
    root = Path(__file__).resolve().parents[1]
    tree = ast.parse((root / "financial_adviser" / "household_ui.py").read_text(encoding="utf-8"))
    node = next(x for x in tree.body if isinstance(x, ast.Assign) and
        any(isinstance(target, ast.Name) and target.id == "_COPY" for target in x.targets))
    return ast.literal_eval(node.value)


def test_all_household_ui_keys_in_each_language():
    copy = _copy()
    assert set(copy) == {"fr", "en", "vi"}
    assert set(copy["fr"]) == set(copy["en"]) == set(copy["vi"])
    for lang in copy:
        assert all(isinstance(text, str) and text.strip() for text in copy[lang].values())


def test_household_labels_use_compatible_variable_placeholders():
    copy = _copy()
    fmt = Formatter()
    for key in copy["fr"]:
        sets = [set(field for _, field, _, _ in fmt.parse(copy[lang][key]) if field)
                for lang in ("fr", "en", "vi")]
        assert sets[0] == sets[1] == sets[2], key