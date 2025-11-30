def get_sus_prompt(input, history="", keywords="", author="user"):
    return (f"""TASK:
Analyze the INPUT from the {author}.
1. If Vendor: Are they consistent? Manipulative? Bluffing?
2. If User: Are they revealing too much? Too soft?
3. If Hint: Did the user follow the advice?

OUTPUT FORMAT:
1. "Decision: [TRUE / BLUFF / WEAKNESS]"
2. Trigger: [Why?]
3. Max 25 words.

HISTORY:
{history}

INPUT ({author}): "{input}"

--- REFERENCE KEYWORDS (USE ONLY IF RELEVANT TO INPUT) ---
{keywords}
""")
