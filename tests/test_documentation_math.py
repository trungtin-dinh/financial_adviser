"""Guard math delimiters in published Markdown for both Streamlit and GitHub.

Both renderers support display math wrapped in $$ delimiters on separate
lines. Literal \\[ ... \\] markers are not reliably parsed by st.markdown.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Documentation"


def test_markdown_display_equations_use_supported_delimiters():
    documents_with_math = 0
    for path in sorted(ROOT.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        assert not any(line.strip() in (r"\[", r"\]") for line in lines), path.name
        delimiters = [index for index, line in enumerate(lines) if line.strip() == "$$"]
        assert len(delimiters) % 2 == 0, (path.name, "unbalanced math blocks")
        if delimiters:
            documents_with_math += 1
        for start, end in zip(delimiters[::2], delimiters[1::2]):
            assert end > start + 1, (path.name, "empty equation")
            assert any(line.strip() for line in lines[start + 1:end])
    assert documents_with_math >= 2


def test_mathematical_documents_keep_their_display_equations():
    expected = {
        "02_MODELES_MATHEMATIQUES.md": 9,
        "21_CYCLE_VIE_BUDGET_FAMILIAL.md": 2,
    }
    for name, count in expected.items():
        source = (ROOT / name).read_text(encoding="utf-8")
        assert sum(line.strip() == "$$" for line in source.splitlines()) == 2 * count, name
