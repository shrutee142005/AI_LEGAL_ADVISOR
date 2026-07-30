import requests


base_url = "http://127.0.0.1:5000"


# Login
login_data = {
    "email": "test@example.com",
    "password": "password123"
}

login_response = requests.post(
    f"{base_url}/api/auth/login",
    json=login_data
)

login_result = login_response.json()

print("Login Status:", login_response.status_code)

token = login_result["access_token"]


# Create conversation
headers = {
    "Authorization": f"Bearer {token}"
}

# Create conversation
conversation_data = {
    "title": "My First Legal Question"
}

conversation_response = requests.post(
    f"{base_url}/api/chat/conversations",
    headers=headers,
    json=conversation_data
)

print("Conversation Status:", conversation_response.status_code)
print("Conversation Response:", conversation_response.json())


# Save conversation ID
conversation_result = conversation_response.json()

conversation_id = conversation_result["conversation"]["id"]

print("Conversation ID:", conversation_id)


# Add message
message_data = {
    "content": "What are my rights as a tenant?"
}

message_response = requests.post(
    f"{base_url}/api/chat/conversations/{conversation_id}/messages",
    headers=headers,
    json=message_data
)

print("Message Status:", message_response.status_code)
print("Message Response:", message_response.json())

# Get chat history
history_response = requests.get(
    f"{base_url}/api/chat/conversations/{conversation_id}/messages",
    headers=headers
)

print("History Status:", history_response.status_code)
print("History Response:", history_response.json())

pdf_path = "legal_documents/sample.pdf"

with open(pdf_path, "rb") as pdf_file:

    upload_response = requests.post(
        f"{base_url}/api/documents/upload",
        headers=headers,
        files={
            "file": pdf_file
        }
    )

print(
    "Upload Status:",
    upload_response.status_code
)

print(
    "Upload Response:",
    upload_response.json()
)