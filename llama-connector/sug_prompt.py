def get_sug_prompt(input, history="", keywords="", author="user"):
    return (f"""TASK:
Suggest the NEXT MOVE.
1. Vendor: Best counter? Leverage?
2. User: Maximize value?
3. Hint: Don't repeat past advice.

OUTPUT FORMAT:
1. "NEXT MOVE: [Advice]"
2. Max 25 words.

HISTORY:
{history}

INPUT ({author}): "{input}"

--- REFERENCE KEYWORDS (USE ONLY IF RELEVANT TO INPUT) ---
{keywords}
""")
