import aiohttp

async def get_relevant_knowledge(pool, company_id):
    """
    Returns relevant knowledge for the company from the API (file storage).
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://localhost:8000/companies/{company_id}/knowledge_file") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    content = data.get("content")
                    if content:
                        return content
    except Exception as e:
        print(f"Error fetching knowledge base from API: {e}")
