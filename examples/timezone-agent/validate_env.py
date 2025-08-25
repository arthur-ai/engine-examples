"""
Environment validation helper for the OpenInference tracing tutorial.
"""

import os

def validate_environment():
    """Validate that all required environment variables are set."""
    required_vars = {
        "ARTHUR_BASE_URL": "Arthur instance URL (e.g., https://app.arthur.ai)",
        "ARTHUR_API_KEY": "Arthur API key from your dashboard",
        "ARTHUR_TASK_ID": "Arthur task ID (ensure task is marked as agentic: is_agentic=True)",
        "OPENAI_API_KEY": "OpenAI API key"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"• {var}: {description}")
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  {var}")
        print("\nPlease update your .env file with the missing values.")
        return False
    
    return True 