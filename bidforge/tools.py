from crewai.tools import tool


@tool("Tender requirement scanner")
def scan_tender_requirements(tender_text: str) -> str:
    """Find likely tender dates and compliance keywords in supplied tender text. No web lookup is performed."""
    terms = [
        "deadline", "closing date", "submission", "eligibility", "evaluation",
        "bid security", "bid bond", "site visit", "pre-bid", "clarification",
        "opening date", "page limit", "penalty", "liability", "intellectual property",
    ]
    lines = [line.strip() for line in tender_text.splitlines() if line.strip()]
    matches = []
    for index, line in enumerate(lines):
        if any(term in line.lower() for term in terms):
            matches.append(f"- {line[:700]}")
    return "\n".join(matches[:100]) if matches else "No matching keywords found. Review the full supplied tender text manually."


@tool("Pricing arithmetic checker")
def check_pricing_arithmetic(items: str) -> str:
    """Check explicitly provided line calculations formatted as description | quantity | unit price. Does not guess missing values."""
    results = []
    for row in items.splitlines():
        columns = [part.strip() for part in row.split("|")]
        if len(columns) != 3:
            continue
        try:
            quantity = float(columns[1].replace(",", ""))
            unit_price = float(columns[2].replace(",", ""))
        except ValueError:
            results.append(f"{columns[0]}: cannot calculate; quantity or unit price is not numeric.")
            continue
        results.append(f"{columns[0]}: {quantity:g} × {unit_price:,.2f} = {quantity * unit_price:,.2f} (before any unspecified taxes/charges).")
    return "\n".join(results) if results else "No complete rows found. Use: item description | numeric quantity | numeric unit price. No missing prices were estimated."
