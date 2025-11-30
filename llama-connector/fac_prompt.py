def get_fac_prompt(input, history="", keywords="", author="user"):
    return (f"""TASK:
List ONLY facts relevant to INPUT.
1. PRICES/SPECS.
2. Verify Vendor claims.
3. Check User facts.
4. Ignore Hints.

OUTPUT FORMAT:
1. Bulleted list starting "FACTS:".
2. If none, "FACTS: None".

HISTORY:
{history}

INPUT ({author}): "{input}"

--- REFERENCE KEYWORDS (USE ONLY IF RELEVANT TO INPUT) ---
{keywords}
""")
