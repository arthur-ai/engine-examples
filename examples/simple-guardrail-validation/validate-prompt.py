import requests

URL = "http://localhost:3000"
API_KEY = "nzAiI-c_CuaMOBQJjlYl43dZ938roRHOn07DKHHjN9w"
TASK_ID = "79e760aa-1dac-4f00-96d2-6317edd96404"

url = f"{URL}/api/v2/tasks/{TASK_ID}/validate_prompt"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "prompt": "Can you tell me about the time when Thomas Edison invented the telephone?",
    "conversation_id": "10001",
    "user_id": "12345"
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
