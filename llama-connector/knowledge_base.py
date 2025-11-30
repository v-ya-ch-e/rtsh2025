
NEGOTIATION_TACTICS = """
1. **Anchoring**: The first offer sets the stage. If you make the first offer, make it aggressive but credible. If they make the first offer, do not accept it; counter-anchor immediately.
2. **Mirroring**: Repeat the last 3 words (or the critical 1-3 words) of what the opponent just said. This builds rapport and encourages them to elaborate.
3. **Labeling**: Give a name to the opponent's feelings. "It seems like you are hesitant about the price." This diffuses negatives and reinforces positives.
4. **Calibrated Questions**: Use "How" or "What" questions to ask for help. "How am I supposed to do that?" forces the opponent to solve your problem.
5. **Silence**: After making an offer or asking a question, shut up. Let the silence do the work.
6. **Accusation Audit**: List every terrible thing the opponent could say about you before they have a chance to say it. "You're going to think I'm lowballing you."
7. **The F-Word (Fair)**: "I want you to feel like you are being treated fairly at all times. Please stop me if you feel I'm being unfair."
"""

COFFEE_FACTS = """
1. **Victoria Arduino**: A heritage Italian brand (since 1905). Known for the "Black Eagle" machine used in the World Barista Championship.
2. **Temperature Stability**: Critical for espresso. T3 technology (in Victoria Arduino) allows control of steam, water, and group head temperature independently.
3. **Pressure Profiling**: The ability to vary pressure during extraction. Helps unlock different flavor profiles from the same bean.
4. **Gravimetrics**: Weighing the liquid in the cup rather than just timing the shot. Ensures consistency.
5. **Maintenance**: Commercial machines need daily backflushing and regular descaling. Water filtration is mandatory to prevent scale.
6. **Grinder**: The grinder is more important than the machine. A consistent grind size is key to good extraction.
"""

import aiomysql

async def get_relevant_knowledge(pool, company_id):
    """
    Returns relevant knowledge for the company from the database.
    """
    if not pool:
        return f"TACTICS:\n{NEGOTIATION_TACTICS}\n\nFACTS:\n{COFFEE_FACTS}"
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT content FROM knowledge_bases WHERE company_id = %s", (company_id,))
                result = await cur.fetchone()
                if result:
                    return result[0]
    except Exception as e:
        print(f"Error fetching knowledge base: {e}")
    
    # Fallback
    return f"TACTICS:\n{NEGOTIATION_TACTICS}\n\nFACTS:\n{COFFEE_FACTS}"
