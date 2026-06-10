URL="http://localhost:3000"
API_KEY="nzAiI-c_CuaMOBQJjlYl43dZ938roRHOn07DKHHjN9w"
TASK_ID="79e760aa-1dac-4f00-96d2-6317edd96404"
INFERENCE_ID="9db01185-1c12-4030-8c66-9f3844e31172"

curl "$URL/api/v2/tasks/$TASK_ID/validate_response/$INFERENCE_ID" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  --data-raw $'{  "response": "Yes, Thomas Edison invented the telephone in 1876, revolutionizing communication with his groundbreaking invention.",  "context": "Alexander Graham Bell is credited with inventing the telephone. He received a patent for his invention in 1876."}'
