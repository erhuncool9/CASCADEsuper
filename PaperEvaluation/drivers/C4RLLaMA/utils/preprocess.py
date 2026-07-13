import re
from typing import Dict, Optional, Tuple

TAG_START = re.compile(r'(?m)^\s*@\w+')

def clean_javadoc(text: str) -> str:
    """
    Remove /** */, leading * and common indentation.
    """
    # Trim /** */ wrappers
    text = re.sub(r'^\s*/\*\*?', '', text.strip(), flags=re.S)
    text = re.sub(r'\*/\s*$', '', text, flags=re.S)

    # Remove leading '*' on each line
    lines = []
    for line in text.splitlines():
        # Strip leading whitespace then optional '*' and one following space
        line = re.sub(r'^\s*\* ?', '', line)
        lines.append(line.rstrip())
    cleaned = "\n".join(lines).strip()

    # Normalize whitespace runs
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    # Preserve paragraph breaks
    cleaned = re.sub(r'[ \t]*\n[ \t]*\n+', '\n\n', cleaned)
    return cleaned

def _split_description_and_tags(text: str) -> Tuple[str, str]:
    """
    Split into (description, tag_block) where tag_block starts at first @tag.
    """
    m = TAG_START.search(text)
    if not m:
        return text.strip(), ""
    return text[:m.start()].rstrip(), text[m.start():].strip()

def _first_sentence(description: str) -> str:
    """
    Heuristic: first sentence ends at the first '.', '!' or '?' followed by space/newline
    or end of string. Handles inline tags like {@code ...}.
    """
    # Collapse inline {@...} to single tokens (avoid periods inside)
    tmp = re.sub(r'\{@[^}]*\}', lambda m: m.group(0).replace('.', '·'), description)

    # Find sentence boundary
    m = re.search(r'(?s)(.*?[.!?])(?:\s+|$)', tmp)
    sent = m.group(1) if m else tmp

    # Restore dots that were masked and tidy spaces/newlines
    sent = sent.replace('·', '.').strip()
    return sent

def _parse_params(tag_block: str) -> Dict[str, str]:
    """
    Parse all @param entries (multi-line friendly).
    """
    params = {}
    for m in re.finditer(
        r'(?ms)^\s*@param\s+(\w+)\s+(.*?)(?=^\s*@\w+|\Z)', tag_block
    ):
        name, desc = m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip()
        params[name] = desc
    return params

def _parse_return(tag_block: str) -> Optional[str]:
    m = re.search(r'(?ms)^\s*@return\s+(.*?)(?=^\s*@\w+|\Z)', tag_block)
    if not m:
        return None
    return re.sub(r'\s+', ' ', m.group(1)).strip() or None

def parse_javadoc(javadoc: str) -> Dict[str, Optional[object]]:
    """
    Parse a Javadoc comment string.

    Returns:
        {
          "summary": str,                    # first sentence of description
          "params": Dict[str, str],          # @param name -> description
          "returns": Optional[str]           # @return description or None
        }
    """
    cleaned = clean_javadoc(javadoc)
    description, tag_block = _split_description_and_tags(cleaned)
    summary = _first_sentence(description) if description else ""
    params = _parse_params(tag_block)
    returns = _parse_return(tag_block)
    return {"summary": summary, "params": params, "returns": returns}
