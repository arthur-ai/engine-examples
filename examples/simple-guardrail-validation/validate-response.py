import requests  
  
URL = "http://localhost:3000"
API_KEY = "nzAiI-c_CuaMOBQJjlYl43dZ938roRHOn07DKHHjN9w"
TASK_ID = "79e760aa-1dac-4f00-96d2-6317edd96404"
INFERENCE_ID = "51c43bfc-e1ac-48e7-8ce1-d9eaada65337"
  
endpoint = f"{URL}/api/v2/tasks/{TASK_ID}/validate_response/{INFERENCE_ID}"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
data = {
    "response": "Yes, Thomas Edison invented the telephone in 1876, revolutionizing communication with his groundbreaking invention.",
    "context": "Alexander Graham Bell is credited with inventing the telephone. He received a patent for his invention in 1876."
} 

response = requests.post(endpoint, headers=headers, json=data)
print(response.status_code)
print(response.json())
