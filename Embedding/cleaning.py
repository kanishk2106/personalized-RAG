import logging
import re

from wordsegment import segment as ws_segment

logger = logging.getLogger(__name__)

PROTECTED_PATTERNS = [
    re.compile(r'\b[\w.+-]+@[\w.-]+\.\w+\b'),
    re.compile(r'\b[A-Z]{2,6}\b'),
    re.compile(r'\b[A-Za-z]+[-_/.][\w\-_/.]{1,30}\b'),
    re.compile(r'\b[A-Za-z]*\d+[A-Za-z0-9]*\b'),
    re.compile(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+){1,3}[A-Z]{0,5}\b'),
    re.compile(r'\b[A-Z][a-z]{2,15}\b'),
]

_UNICODE_REPLACEMENTS = {
    "\u00a0": " ",
    "\ufeff": "",
    "\u2011": "-",
    "\u2012": "-",
    "\u2013": "-",
    "\u2014": "—",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2026": "...",
}


def normalize_unicode(text: str) -> str:
    for src, dst in _UNICODE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def remove_cid_artifacts(text: str) -> str:
    return re.sub(r"\(cid:\d+\)", "", text)


def remove_stray_digit_markers(text: str) -> str:
    return re.sub(r"(?<=[a-zA-Z])\s+\d{1,2}\s+(?=[a-zA-Z])(?!\s*(?:years|months|days|kg|lbs)\b)", " ", text)


_MIN_GLUED_LEN = 10


def _segment_glued_run(match: re.Match) -> str:
    token = match.group(0)
    if len(token) < _MIN_GLUED_LEN:
        return token
    starts_upper = token[0].isupper()
    segmented = ws_segment(token.lower())
    if len(segmented) > 1:
        result = " ".join(segmented)
        if starts_upper:
            result = result[0].upper() + result[1:]
        logger.debug("Segmented glued run: %r -> %r", token, result)
        return result
    return token


def fix_concatenated_words(text: str) -> str:
    protected: list[str] = []

    def stash(match: re.Match) -> str:
        idx = len(protected)
        protected.append(match.group(0))
        return f"\ue000{idx}\ue001"

    combined = re.compile(
        "|".join(f"(?:{p.pattern})" for p in PROTECTED_PATTERNS)
    )
    text = combined.sub(stash, text)
    text = re.sub(r"([a-zA-Z])([,;:])([a-zA-Z])", r"\1\2 \3", text)
    text = re.sub(r"\b[a-zA-Z]{10,}\b", _segment_glued_run, text)
    for idx in range(len(protected) - 1, -1, -1):
        text = text.replace(f"\ue000{idx}\ue001", protected[idx])
    return text


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()



def detect_repeating_headers(pages_text: list[str], min_occurrences: int = 3) -> list[str]:
    from collections import Counter
    line_counts: Counter[str] = Counter()
    margin = 3
    for page_text in pages_text:
        lines = page_text.splitlines()
        total_lines = len(lines)
        unique_margin_lines = set() 
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and len(stripped) > 3:
                is_at_top = i < margin
                is_at_bottom = i >= (total_lines - margin)
                if is_at_top or is_at_bottom:
                    unique_margin_lines.add(stripped)
        for line in unique_margin_lines:
            line_counts[line] += 1
    return [line for line, count in line_counts.items() if count >= min_occurrences]

def remove_page_artifacts(text: str, headers_to_strip: list[str] | None = None) -> str:
    lines = text.splitlines()
    cleaned_lines: list[str] = []
    total_lines = len(lines)
    margin = 5  
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"\d+\s*of\s*\d+", stripped, flags=re.IGNORECASE):
            continue
        if re.fullmatch(r"\d{1,3}", stripped):
            continue
        if headers_to_strip and stripped in headers_to_strip:
            is_at_top = i < margin
            is_at_bottom = i >= (total_lines - margin)
            if is_at_top or is_at_bottom:
                continue 
            else:
                pass 
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


def _collapse_newlines_smartly(text: str) -> str:
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"(\w)\n(\w)", r"\1 \2", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    return text


def clean_page_text(text: str, headers_to_strip: list[str] | None = None) -> str:
    text = normalize_unicode(text)
    text = remove_cid_artifacts(text)
    text = remove_page_artifacts(text, headers_to_strip)
    text = _collapse_newlines_smartly(text)
    text = fix_concatenated_words(text)
    text = normalize_whitespace(text)
    return text