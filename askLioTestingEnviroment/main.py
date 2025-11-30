import requests

API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = 823044  # Your team ID from the dashboard

# 1. List vendors
vendors_response = requests.get(
    f"{API_BASE}/vendors/",
    params={"team_id": TEAM_ID}
)
vendors = vendors_response.json()
vendor_id = vendors[5]["id"]

# 2. Create conversation
conversation_response = requests.post(
    f"{API_BASE}/conversations/",
    params={"team_id": TEAM_ID},
    json={
        "vendor_id": vendor_id,
        "title": "Price Negotiation"
    }
)
conversation = conversation_response.json()
conversation_id = conversation["id"]

# 3. Send message and get AI response (uses multipart/form-data for file support)
message_response = requests.post(
    f"{API_BASE}/messages/{conversation_id}",
    data={"content": "I need 100 units. What's your best price?"}
    # To attach files: files={"files": open("document.pdf", "rb")}
)
ai_response = message_response.json()
print(f"Vendor says: {ai_response['content']}")

# 4. Continue negotiation loop
while True:
    user_input = input("You: ")
    if user_input.lower() in ['quit', 'exit']:
        break

    response = requests.post(
        f"{API_BASE}/messages/{conversation_id}",
        data={"content": user_input}
    )
    ai_msg = response.json()
    print(f"Vendor: {ai_msg['content']}")
