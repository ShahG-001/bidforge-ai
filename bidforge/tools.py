from crewai.tools import tool
import csv
from io import StringIO


def scan_tender_requirements_text(tender_text: str) -> str:
    """Deterministically find requirement-bearing source lines without an LLM tool call."""
    terms = [
        "deadline", "closing date", "submission", "eligibility", "evaluation",
        "bid security", "bid bond", "site visit", "pre-bid", "clarification",
        "opening date", "page limit", "penalty", "liability", "intellectual property",
        "mandatory", "deliverable", "pricing", "tax", "insurance", "certificate",
    ]
    lines = [line.strip() for line in tender_text.splitlines() if line.strip()]
    matches = []
    for line in lines:
        if any(term in line.lower() for term in terms):
            matches.append(f"- {line[:500]}")
    return "\n".join(matches[:80]) if matches else "No matching keywords found. Review the full supplied tender text manually."


def check_pricing_arithmetic_rows(items: str) -> str:
    """Calculate totals only for explicitly supplied description|quantity|unit price rows."""
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


def check_pricing_csv_arithmetic(pricing_csv: str) -> str:
    """Use CSV values only when quantity and rate columns are both provided."""
    try:
        rows = list(csv.DictReader(StringIO(pricing_csv)))
    except Exception:
        return "Pricing arithmetic not checked: supplied pricing table could not be parsed."
    if not rows:
        return "Pricing arithmetic not checked: no pricing rows were supplied."
    keys = {key.strip().lower(): key for key in rows[0] if key}
    quantity_key = next((keys[name] for name in ("quantity", "qty") if name in keys), None)
    rate_key = next((keys[name] for name in ("unit price", "rate", "unit rate") if name in keys), None)
    item_key = next((keys[name] for name in ("resource", "item", "description") if name in keys), None)
    if not quantity_key or not rate_key:
        return "Pricing arithmetic not checked: add Quantity and Rate/Unit Price columns to calculate line totals. No amounts were inferred."
    formatted = []
    for row in rows:
        formatted.append(" | ".join(str(row.get(key, "")) for key in (item_key, quantity_key, rate_key)))
    return check_pricing_arithmetic_rows("\n".join(formatted))


@tool("Tender requirement scanner")
def scan_tender_requirements(tender_text: str) -> str:
    """Find likely tender dates and compliance keywords in supplied tender text. No web lookup is performed."""
    return scan_tender_requirements_text(tender_text)


@tool("Pricing arithmetic checker")
def check_pricing_arithmetic(items: str) -> str:
    """Check explicitly provided line calculations formatted as description | quantity | unit price. Does not guess missing values."""
    return check_pricing_arithmetic_rows(items)
