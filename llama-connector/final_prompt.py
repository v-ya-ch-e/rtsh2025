def get_final_prompt(input, sus, sug, fac, history="", author="user"):
    return (f"""TASK:
Decide the SINGLE most important thing to tell the user.
- If NO action is needed, output "NO_RESPONSE".
- If CRITICAL facts/bluffs found, WARN them.
- If a tactic fits perfectly, SUGGEST it.
- Be cold, calculating, strategic. NO sales talk. NO repetition.

OUTPUT FORMAT:
1. JSON: {{"MESSAGE_COLOR": "red/green/blue/yellow", "MESSAGE": "Text (max 25 words) OR NO_RESPONSE"}}
2. NO THOUGHTS. ONLY JSON.

HISTORY:
{history}

ANALYSIS:
- BLUFF: {sus}
- SUGGESTION: {sug}
- FACTS: {fac}

INPUT ({author}): "{input}"
""")
