"""Unit tests for limited rich-text sanitization."""

from app.utils.rich_text import sanitize_rich_text


def test_sanitize_rich_text_keeps_supported_tables_and_formatting():
    source = (
        "<p><strong>Summary</strong></p>"
        '<table><colgroup><col width="120"><col width="240"></colgroup>'
        '<tbody><tr><th colspan="2">Header</th></tr>'
        "<tr><td>A</td><td><em>B</em></td></tr></tbody></table>"
    )

    assert sanitize_rich_text(source) == source


def test_sanitize_rich_text_removes_unsafe_markup_and_content():
    source = (
        '<div class="ignored">Safe<script>alert("bad")</script>'
        '<img src=x onerror="bad()"><span>Text</span></div>'
    )

    assert sanitize_rich_text(source) == "<div>SafeText</div>"


def test_sanitize_rich_text_removes_invalid_table_column_widths():
    source = (
        '<table><colgroup><col width="20"><col width="6000">'
        '<col width="240px"><col width="240"></colgroup>'
        "<tbody><tr><td>A</td><td>B</td><td>C</td><td>D</td></tr></tbody></table>"
    )

    assert sanitize_rich_text(source) == (
        '<table><colgroup><col><col><col><col width="240"></colgroup>'
        "<tbody><tr><td>A</td><td>B</td><td>C</td><td>D</td></tr></tbody></table>"
    )
