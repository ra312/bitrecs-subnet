#!/usr/bin/env python3
"""parse_log.py

Extract structured information from bittensor miner logs.
"""

from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import ast
from typing import List, Dict, Optional

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
FORWARD_RE = re.compile(r"FORWARD PASS\s+(?!RESULT)(\S+)")
PERSONA_RE = re.compile(r"Persona:\s*([^\s]+)")
SEASON_RE = re.compile(r"Season\s+([^\s]+)")
VALUES_RE = re.compile(r"Values:\s*(.*)")
PROFILE_RE = re.compile(r"'profile': '([^']+)'")
PROMPT_START_RE = re.compile(r"Prompt:\s*(# SCENARIO.*)")
LLM_RESP_RE = re.compile(r"LLM response:\s*(\[.*)$")
CONTEXT_RE = re.compile(r"<context>\s*(\[[\s\S]*?)\s*</context>", re.MULTILINE)
# New regex patterns for additional metadata
LLM_PROVIDER_RE = re.compile(r"do_work LLM server:\s*(\S+)")
MODEL_SLUG_RE   = re.compile(r"do_work LLM model:\s*(\S+)")
USER_PROFILE_RE = re.compile(r"do_work profile:\s*(UserProfile\(.*\))")

# Regex to extract pieces from the prompt header (no <context>)
PERSONA_TAG_RE   = re.compile(r"<persona>([^<]+)</persona>")
SKU_TAG_RE       = re.compile(r"SKU <sku>([^<]+)</sku>")
SKU_INFO_TAG_RE  = re.compile(r"<sku_info>([^<]+)</sku_info>")
SEASON_TAG_RE    = re.compile(r"Current season:\s*<season>([^<]+)</season>")
DATE_LINE_RE     = re.compile(r"Today's date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})")


#!/usr/bin/env python3
"""
prompt_builder.py

Builds the prompt header used by the miner **without** the <context> section.
You can pass the header onward as-is, or append a JSON product list between
'<context>' … '</context>' before sending it to the LLM.

Example
-------
python prompt_builder.py \
    --persona ecommerce_retail_store_manager \
    --sku MJ01 \
    --sku-info "Beaumont Summit Kit - Jackets" \
    --season "spring/summer" \
    --date 2025-07-11
"""

import argparse
from datetime import date


TEMPLATE = """# SCENARIO
A shopper is viewing a product with SKU <sku>{sku}</sku> named <sku_info>{sku_info}</sku_info> on your e-commerce store.
They are looking for complimentary products to add to their cart.
You will build a recommendation set with no duplicates based on the provided context and your persona qualities.

# YOUR PERSONA
<persona>{persona}</persona>

<core_attributes>
You embody: {core_attributes}
Your mindset: {mindset}
Your expertise: {expertise}
Core values: {core_values}
</core_attributes>

# YOUR ROLE:
- Recommend **5** complimentary products (A -> X,Y,Z)
- Increase average order value and conversion rate
- Use deep product catalog knowledge
- Understand product attributes and revenue impact
- Avoid variant duplicates (same product in different colors/sizes)
- Consider seasonal relevance

Current season: <season>{season}</season>
Today's date: {today}

# TASK
Given a product SKU <sku>{sku}</sku> select **5** complementary unique products from the context.
Use your persona qualities to THINK about which products to select, but return ONLY a JSON array.
Evaluate each product name and price fields before making your recommendations.
The name field is the most important attribute followed by price.
The product name will often contain important information like which category it belongs to, sometimes denoted by | characters indicating the category hierarchy.
Leverage the complete information ecosystem - product catalog, user context, seasonal trends, and your persona's core values - to deliver complimentary recommendations.
Apply comprehensive analysis using all available inputs: product attributes from the context, user cart history, seasonal relevance, pricing considerations and your persona's core values to create a cohesive recommendation set.
Utilize your core_attributes to make the best recommendations.
Do **not** recommend products that are already in the cart.

# INPUT
Query SKU: <sku>{sku}</sku><sku_info>{sku_info}</sku_info>

Current cart:
<cart>
[]
</cart>

"""

def build_prompt(
    persona: str,
    sku: str,
    sku_info: str,
    season: str,
    today: str | None = None,
    core_attributes: str = "an experienced e-commerce retail store manager with a strategic focus on optimizing sales, customer satisfaction, and inventory turnover across a diverse marketplace",
    mindset: str = "professional, practical, results-driven",
    expertise: str = "Provide balanced recommendations that align with business goals, customer preferences, and current market trends. Include actionable insights for product selection",
    core_values: str = "sales optimization, customer satisfaction, inventory management",
) -> str:
    """Return the prompt header (no <context>) as a single string."""
    return TEMPLATE.format(
        persona=persona,
        sku=sku,
        sku_info=sku_info,
        season=season,
        today=today or date.today().isoformat(),
        core_attributes=core_attributes,
        mindset=mindset,
        expertise=expertise,
        core_values=core_values,
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate prompt header without context.")
    ap.add_argument("--persona", required=True)
    ap.add_argument("--sku", required=True)
    ap.add_argument("--sku-info", required=True)
    ap.add_argument("--season", required=True)
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (defaults to today)")
    args = ap.parse_args()

    prompt_text = build_prompt(
        persona=args.persona,
        sku=args.sku,
        sku_info=args.sku_info,
        season=args.season,
        today=args.date,
    )
    print(prompt_text)
    
def strip_ansi(text: str) -> str:
    """Remove ANSI colour codes."""
    return ANSI_RE.sub("", text)


def extract_context(prompt: str):
    """Extract the JSON product context array from a prompt string.

    The prompt contains a section delimited by <context> ... </context> which
    encloses a JSON array of product dictionaries.

    If parsing succeeds, return the list; otherwise return the raw matched
    string (or an empty list if not found).
    """
    m = CONTEXT_RE.search(prompt)
    if not m:
        return []  # context not present
    ctx_raw = m.group(1).strip()
    try:
        return json.loads(ctx_raw)
    except json.JSONDecodeError:
        # fallback: return raw string to avoid data loss
        return ctx_raw


# ---------------------------------------------------------------------------
# Individual parameter extraction helpers
# ---------------------------------------------------------------------------

def extract_persona(prompt: str) -> str:
    """Return persona tag inside <persona>…</persona>."""
    m = PERSONA_TAG_RE.search(prompt)
    return m.group(1) if m else ""


def extract_sku(prompt: str) -> str:
    """Return first SKU code inside 'SKU <sku>…</sku>'."""
    m = SKU_TAG_RE.search(prompt)
    return m.group(1) if m else ""


def extract_sku_info(prompt: str) -> str:
    """Return text inside <sku_info>…</sku_info>."""
    m = SKU_INFO_TAG_RE.search(prompt)
    return m.group(1) if m else ""


def extract_season(prompt: str) -> str:
    """Return season string from 'Current season: <season>…</season>'."""
    m = SEASON_TAG_RE.search(prompt)
    return m.group(1) if m else ""


def extract_date(prompt: str) -> str:
    """Return date string YYYY-MM-DD from 'Today's date: …'."""
    m = DATE_LINE_RE.search(prompt)
    return m.group(1) if m else ""

# ---------------------------------------------------------------------------
# Existing utilities
# ---------------------------------------------------------------------------

def parse_llm_response(llm_response_raw: str):
    """Convert the raw validator LLM response string (python list / single quotes)
    into a JSON-serialisable Python object (list of dicts).
    If parsing fails, return the raw string.
    """
    try:
        data = ast.literal_eval(llm_response_raw)
        # ensure each element is a dict with expected keys
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return llm_response_raw


def process_log(path: Path) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    current: Optional[Dict[str, str]] = None
    capturing_prompt = False
    prompt_lines: List[str] = []
    llm_response_raw: Optional[str] = None

    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for raw_line in fh:
            line = strip_ansi(raw_line).rstrip("\n")

            # Detect start of new FORWARD PASS block
            m = FORWARD_RE.search(line)
            if m:
                # flush the previous block if one existed
                if current is not None:
                    if prompt_lines:
                        current["prompt"] = "\n".join(prompt_lines)
                    if llm_response_raw:
                        current["llm_response"] = parse_llm_response(llm_response_raw)
                    results.append(current)
                # start new block
                current = {
                    "query": m.group(1),
                    "persona": "",
                    "season": "",
                    "core_values": "",
                    "prompt": "",
                    "llm_response": "",
                    "llm_provider": "",
                    "model_slug": "",
                    "user_profile": "",
                }
                capturing_prompt = False
                prompt_lines = []
                llm_response_raw = None
                continue  # go to next line

            if current is None:
                continue  # skip lines until we hit the first block

            # Persona
            if not current["persona"]:
                m = PERSONA_RE.search(line)
                if m:
                    current["persona"] = m.group(1)
                else:
                    m2 = PROFILE_RE.search(line)
                    if m2:
                        current["persona"] = m2.group(1)

            # Season
            if not current["season"]:
                m = SEASON_RE.search(line)
                if m:
                    current["season"] = m.group(1)

            # Core values
            if not current["core_values"]:
                m = VALUES_RE.search(line)
                if m:
                    current["core_values"] = m.group(1).strip()

            # LLM provider
            if not current["llm_provider"]:
                m = LLM_PROVIDER_RE.search(line)
                if m:
                    current["llm_provider"] = m.group(1)

            # Model slug
            if not current["model_slug"]:
                m = MODEL_SLUG_RE.search(line)
                if m:
                    current["model_slug"] = m.group(1)

            # User profile (full string representation)
            if not current["user_profile"]:
                m = USER_PROFILE_RE.search(line)
                if m:
                    current["user_profile"] = m.group(1)

            # Prompt start
            if not capturing_prompt:
                m = PROMPT_START_RE.search(line)
                if m:
                    capturing_prompt = True
                    prompt_lines.append(m.group(1))
                    continue

            # Capture prompt lines until OUTPUT REQUIREMENTS line
            if capturing_prompt:
                if "OUTPUT REQUIREMENTS" in line:
                    capturing_prompt = False
                else:
                    prompt_lines.append(line.strip())

            # Capture validator response line
            if llm_response_raw is None:
                m = LLM_RESP_RE.search(line)
                if m:
                    llm_response_raw = m.group(1).strip()

    # flush last block
    if current is not None:
        if prompt_lines:
            current["prompt"] = "\n".join(prompt_lines)
        if llm_response_raw:
            current["llm_response"] = parse_llm_response(llm_response_raw)
        results.append(current)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse bittensor miner log for structured prompt information.")
    parser.add_argument("logfile", type=Path, help="Path to log file (e.g. ckli09-m-16897-out.log)")
    parser.add_argument("-o", "--output", type=Path, help="Write JSON output to this file instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    blocks = process_log(args.logfile)
    json_kw = dict(indent=2) if args.pretty else {}

    if args.output:
        with args.output.open("w", encoding="utf-8") as out_f:
            json.dump(blocks, out_f, **json_kw)
    else:
        json.dump(blocks, fp=sys.stdout, **json_kw)


if __name__ == "__main__":
    import sys  # placed here to avoid issues in typing above
    main()

