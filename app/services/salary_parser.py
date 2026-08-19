"""
Salary Parser

Best-effort regex-based parsing of salary text into numeric min/max bounds.

Supported patterns:
  - "$150,000"                       -> (150000, None)
  - "$120K - $150K"                  -> (120000, 150000)
  - "150000-180000"                  -> (150000, 180000)
  - "150000 - 180000"                -> (150000, 180000)
  - "$140k/year"                     -> (140000, None)
  - "Competitive"                    -> (None, None)  -- no confident match
  - "DOE", "Negotiable"              -> (None, None)
"""

import re
from typing import Optional, Tuple


def parse_salary_text(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse raw salary text and return (min_salary, max_salary) in USD.

    Returns (None, None) if the text doesn't confidently match a known
    pattern. This is intentional: a posting whose salary text doesn't
    parse simply has no numeric value; it's not excluded from search,
    it just won't match a numeric range filter.

    Rules:
    - Patterns must explicitly contain numeric values; vague terms
      like 'Competitive', 'DOE', 'Negotiable' return (None, None).
    - If only one number is found, it's treated as salary_min (max=None).
    - If two numbers are found, they are assigned as min/max in order.
    - '$K' / 'k' suffix (e.g. '120K') is supported -- value is in
      thousands.
    - Commas in numbers are handled.
    - Currency symbol '$' is optional if a number is already present.
    - A bare number must be at least 3 digits to be treated as a
      salary -- this avoids misinterpreting stray digits in unrelated
      text (e.g. a pay-grade code like "Grade 5") as a dollar figure.
    """
    if not isinstance(text, str):
        return None, None

    text_stripped = text.strip()
    if not text_stripped:
        return None, None

    text_lower = text_stripped.lower()

    # Vague terms that should not parse as a numeric salary, checked
    # as substrings (not just exact matches) so that vague language
    # mixed with unrelated digits elsewhere in the text is still
    # correctly rejected rather than falling through to a fallback
    # pattern below.
    vague_terms = (
        "competitive",
        "doe",
        "negotiable",
        "commensurate",
    )

    if any(term in text_lower for term in vague_terms):
        return None, None

    # Pattern: "$120K - $150K"  (K-suffixed two-range, must be checked
    # early before the single-value fallback intercepts just "$120K")
    two_range_k = re.findall(
        r"\$?\s*([0-9][0-9,]*)K\s*-\s*\$?\s*([0-9][0-9,]*)K",
        text_stripped,
        re.IGNORECASE,
    )
    if two_range_k:
        try:
            min_val = int(two_range_k[0][0].replace(",", "")) * 1000
            max_val = int(two_range_k[0][1].replace(",", "")) * 1000
            return min_val, max_val
        except ValueError:
            pass

    # Pattern: "$NNN,NNN - $NNN,NNN" or "NNN,NNN - NNN,NNN"
    two_range = re.findall(
        r"\$?\s*([0-9][0-9,]*)\s*-\s*\$?\s*([0-9][0-9,]*)",
        text_stripped,
    )
    if two_range:
        try:
            min_str, max_str = two_range[0]
            min_val = int(min_str.replace(",", ""))
            max_val = int(max_str.replace(",", ""))
            return min_val, max_val
        except ValueError:
            pass

    # Pattern: "NNN-NNN" (e.g. "150000-180000") without commas
    single_range = re.findall(
        r"\b([0-9]{3,5})-([0-9]{3,5})\b",
        text_stripped,
    )
    if single_range:
        try:
            min_val = int(single_range[0][0])
            max_val = int(single_range[0][1])
            return min_val, max_val
        except ValueError:
            pass

    # Pattern: single value with a K suffix, e.g. "$120K", "140k/year"
    single_value_k = re.findall(
        r"\$?\s*([0-9][0-9,]*)\s*[kK]\b",
        text_stripped,
    )
    if single_value_k:
        try:
            val = int(single_value_k[0].replace(",", "")) * 1000
            return val, None
        except ValueError:
            pass

    # Pattern: a bare number, at least 3 digits (e.g. "75000",
    # "$150,000"). The 3-digit minimum is deliberate -- without it, a
    # stray single digit anywhere in unrelated text (an internal pay
    # grade, a requisition number fragment, etc.) would be misread as
    # a salary.
    single_number = re.findall(
        r"\$?\s*([0-9][0-9,]{2,})\b",
        text_stripped,
    )
    if single_number:
        try:
            val = int(single_number[0].replace(",", ""))
            return val, None
        except ValueError:
            pass

    # No confident pattern matched
    return None, None


def format_salary_range(
    min_val: int | None,
    max_val: int | None,
) -> str:
    """
    Format a parsed (min, max) salary range back into a display string.
    Used for debugging / display purposes only.
    """
    if min_val is not None and max_val is not None:
        if min_val == max_val:
            return f"${min_val:,}"
        return f"${min_val:,} - ${max_val:,}"

    if min_val is not None:
        return f"${min_val:,}"

    if max_val is not None:
        return f"${max_val:,}"

    return ""