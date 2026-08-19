"""
Test Salary Parser

Verifies salary text parsing against supported patterns, vague
language, and edge cases -- including the misparse guard against
short unrelated numbers (e.g. internal pay-grade codes).
"""

from app.services.salary_parser import format_salary_range, parse_salary_text


def check(
    description: str,
    text: str | None,
    expected_min: int | None,
    expected_max: int | None,
) -> None:
    """
    Run a single parser test case, raising on mismatch.
    """

    actual_min, actual_max = parse_salary_text(text)  # type: ignore[arg-type]

    if actual_min != expected_min or actual_max != expected_max:
        raise RuntimeError(
            f"{description}: expected min={expected_min}, "
            f"max={expected_max}, got min={actual_min}, "
            f"max={actual_max} (text={text!r})"
        )

    print(f"{description:<45} : Passed")


def main() -> None:
    """
    Test the salary parser against real and edge-case inputs.
    """

    print()
    print("# Salary Parser Test")
    print()

    check("$150,000 (single with comma)", "$150,000", 150000, None)
    check("$120K - $150K (K suffix range)", "$120K - $150K", 120000, 150000)
    check("150000-180000 (numeric range)", "150000-180000", 150000, 180000)
    check("$75000 (single no comma)", "$75000", 75000, None)
    check("120000 (single no symbol)", "120000", 120000, None)
    check("140k/year (lowercase k, suffix text)", "140k/year", 140000, None)

    check("Competitive", "Competitive", None, None)
    check("DOE", "DOE", None, None)
    check("Negotiable", "Negotiable", None, None)
    check("Commensurate with experience", "Commensurate with experience", None, None)

    check("empty string", "", None, None)
    check("None input", None, None, None)
    check("just text, no numbers", "some random text", None, None)

    # Regression check: a short, unrelated number embedded in text
    # (e.g. an internal pay-grade code) must not be misread as a
    # salary -- this is the bug the 3-digit minimum guards against.
    check("Grade 5 (short number, not a salary)", "Grade 5", None, None)
    check("Level 3 role", "Level 3 role", None, None)

    print()
    print("Format tests:")
    print(f"  format(150000, None)   = '{format_salary_range(150000, None)}'")
    print(f"  format(120000, 150000) = '{format_salary_range(120000, 150000)}'")
    print(f"  format(None, None)     = '{format_salary_range(None, None)}'")
    print(f"  format(150000, 150000) = '{format_salary_range(150000, 150000)}'")

    print()
    print("Salary parser test passed.")


if __name__ == "__main__":
    main()