import html
import difflib
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter

def _get_lexer(filename_or_lang):
    """Attempt to find a lexer by filename, then by language name."""
    try:
        return get_lexer_for_filename(filename_or_lang)
    except Exception:
        try:
            return get_lexer_by_name(filename_or_lang)
        except Exception:
            return TextLexer()

def get_highlighted_diff(old_text, new_text, filename, full_context=False):
    """
    Calculates the diff between two strings and applies Pygments syntax highlighting.
    Returns a list of dictionaries ready for the frontend.
    """
    old_text = old_text or ""
    new_text = new_text or ""

    old_raw_lines = old_text.splitlines()
    new_raw_lines = new_text.splitlines()

    if full_context:
        # Skip Pygments for Project Starter (Markdown/text) to keep UI clean and fast
        old_html_lines = [html.escape(line) for line in old_raw_lines]
        new_html_lines = [html.escape(line) for line in new_raw_lines]
    else:
        lexer = _get_lexer(filename)

        # nowrap=True prevents Pygments from wrapping the output in <pre> tags
        formatter = HtmlFormatter(nowrap=True)

        # Highlight the full texts first, then split into lines
        old_html_lines = highlight(old_text, lexer, formatter).splitlines()
        new_html_lines = highlight(new_text, lexer, formatter).splitlines()

        # Safety fallback: If Pygments consumed newlines weirdly, fallback to basic HTML escaping
        if len(old_html_lines) != len(old_raw_lines) or len(new_html_lines) != len(new_raw_lines):
            old_html_lines = [html.escape(line) for line in old_raw_lines]
            new_html_lines = [html.escape(line) for line in new_raw_lines]

    # Calculate the diff based on the RAW text (so HTML tags don't break the diff math)
    matcher = difflib.SequenceMatcher(None, old_raw_lines, new_raw_lines)
    diff_rows = []

    if full_context:
        opcodes_groups = [matcher.get_opcodes()]
    else:
        opcodes_groups = matcher.get_grouped_opcodes(3)

    for group in opcodes_groups:
        if not full_context:
            i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
            diff_rows.append({
                "type": "header",
                "prefix": "@@",
                "html": html.escape(f"-{i1+1},{i2-i1} +{j1+1},{j2-j1} @@")
            })

        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for i in range(i1, i2):
                    diff_rows.append({"type": "context", "prefix": " ", "html": old_html_lines[i]})
            elif tag == 'delete':
                for i in range(i1, i2):
                    diff_rows.append({"type": "remove", "prefix": "-", "html": old_html_lines[i]})
            elif tag == 'insert':
                for j in range(j1, j2):
                    diff_rows.append({"type": "add", "prefix": "+", "html": new_html_lines[j]})
            elif tag == 'replace':
                for i in range(i1, i2):
                    diff_rows.append({"type": "remove", "prefix": "-", "html": old_html_lines[i]})
                for j in range(j1, j2):
                    diff_rows.append({"type": "add", "prefix": "+", "html": new_html_lines[j]})

    return diff_rows

def get_highlighted_code(text, filename):
    """
    Applies syntax highlighting to a single block of code.
    Returns a list of HTML lines.
    """
    lexer = _get_lexer(filename)

    formatter = HtmlFormatter(nowrap=True)
    html_lines = highlight(text, lexer, formatter).splitlines()
    return html_lines

def get_pygments_css():
    """Returns the CSS classes needed to render the Pygments HTML."""
    # 'monokai' is a great dark theme for CodeMerger's aesthetic
    return HtmlFormatter(style='monokai').get_style_defs('.highlight')