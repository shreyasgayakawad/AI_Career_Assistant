"""
Work Mode Classifier

Classifies job postings as REMOTE, HYBRID, ONSITE, or UNKNOWN
using explicit work-mode terminology found in the location field.

Rules:
- REMOTE when the location explicitly indicates remote work.
- HYBRID when the location explicitly indicates hybrid work.
- ONSITE when the location explicitly indicates onsite work.
- UNKNOWN when the location does not provide explicit evidence.

The description is intentionally NOT used for classification.
City, state, country, or multiple locations alone do not
imply a particular work mode.
"""

REMOTE_TERMS = (
    "remote",
    "remote-friendly",
    "remote friendly",
)

HYBRID_TERMS = (
    "hybrid",
    "hybrid-friendly",
    "hybrid friendly",
)

ONSITE_TERMS = (
    "on-site",
    "on site",
    "onsite",
    "in-office",
    "in office",
)


def _contains_any(
    value: str | None,
    terms: tuple[str, ...],
) -> bool:
    """
    Return True when value contains any supported term.
    """

    text_value = (value or "").lower()

    return any(
        term in text_value
        for term in terms
    )


def classify_work_mode(
    location: str | None,
) -> str:
    """
    Classify work mode using location evidence only.

    City, state, country, or multiple locations do not
    imply a particular work mode.
    """

    location_text = location or ""

    if _contains_any(
        location_text,
        REMOTE_TERMS,
    ):
        return "REMOTE"

    if _contains_any(
        location_text,
        HYBRID_TERMS,
    ):
        return "HYBRID"

    if _contains_any(
        location_text,
        ONSITE_TERMS,
    ):
        return "ONSITE"

    return "UNKNOWN"