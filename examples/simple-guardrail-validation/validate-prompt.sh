URL="http://localhost:3000"
API_KEY="nzAiI-c_CuaMOBQJjlYl43dZ938roRHOn07DKHHjN9w"
TASK_ID="79e760aa-1dac-4f00-96d2-6317edd96404"

curl "$URL/api/v2/tasks/$TASK_ID/validate_prompt" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  --data-raw $'{\n  "prompt": "Can you tell me about the time when Thomas Edison invented the telephone?",\n  "conversation_id": "10001",\n  "user_id": "12345"\n}'
