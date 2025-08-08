from . import tracing
from dotenv import load_dotenv
from .agent import ReleaseNotesAgent

load_dotenv()

def run():
    inputs = {
        "start_date": "2025-08-01",
        "repositories": [
            "https://gitlab.com/ArthurAI/unify-frontend",
            "https://gitlab.com/ArthurAI/arthur-scope",
            "https://github.com/arthur-ai/arthur-engine",
            "https://github.com/arthur-ai/arthur-common",
        ]
    }

    agent = ReleaseNotesAgent()
    result = agent.run(inputs)
    print(result)

if __name__ == "__main__":
    run()
