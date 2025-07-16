from .crew import ReleaseNotesCrew


def run():
    inputs = {
        "start_date": "2025-07-01",
        "repositories": [
            "https://gitlab.com/ArthurAI/unify-frontend",
            "https://gitlab.com/ArthurAI/arthur-scope",
            "https://github.com/arthur-ai/arthur-engine",
            "https://github.com/arthur-ai/arthur-common",
        ]
    }
    ReleaseNotesCrew().crew().kickoff(inputs)


if __name__ == "__main__":
    run()