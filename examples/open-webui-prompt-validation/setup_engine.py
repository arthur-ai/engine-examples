import requests
import urllib.parse
import datetime
ENGINE_BASE_URL = "http://localhost:3030"
ENGINE_ADMIN_KEY = "admin"
ENGINE_API_KEY = "wIkkggwzSj4X5elVHc3CsQMFxzJaOInclAh6l9_TvzE"
TASK_ID = "47403f8c-5c7b-40a7-b385-05e859f579ee"


def get_engine_admin_client():
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {ENGINE_ADMIN_KEY}",
        "Content-Type": "application/json"
    })
    session.base_url = ENGINE_BASE_URL.rstrip("/")
    return session


def get_engine_client():
    if not ENGINE_API_KEY:
        raise Exception("API Key not set")

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {ENGINE_API_KEY}",
        "Content-Type": "application/json"
    })
    session.base_url = ENGINE_BASE_URL.rstrip("/")
    return session


def create_api_key():
    global ENGINE_API_KEY

    if ENGINE_API_KEY:
        return

    admin_client = get_engine_admin_client()
    description = "API Key for Test Task"
    roles = [
        "ORG-ADMIN"
    ]
    r = admin_client.post(
        f"{admin_client.base_url}/auth/api_keys",
        json = {
            "description": description,
            "roles": roles
        },
        verify=False
    )
    r.raise_for_status()

    ENGINE_API_KEY = r.json()["key"]
    print(f"Created API Key: {ENGINE_API_KEY}")


def create_task(task_name):
    engine_client = get_engine_client()
    r = engine_client.post(
        f"{engine_client.base_url}/api/v2/tasks",
        json = {"name": task_name},
        verify=False
    )
    r.raise_for_status()
    return r.json()


def get_task(task_id):
    engine_client = get_engine_client()
    r = engine_client.get(
        f"{engine_client.base_url}/api/v2/tasks/{task_id}",
        verify=False
    )
    r.raise_for_status()
    return r.json()

def create_task_rule(task_id, rule_config):
    engine_client = get_engine_client()
    r = engine_client.post(
        f"{engine_client.base_url}/api/v2/tasks/{task_id}/rules",
        json=rule_config,
        verify=False
    )
    r.raise_for_status()
    return r.json()

def query_inferences(task_id):
    engine_client = get_engine_client()
    all_inferences = []
    page = 0
    while True:
        try:
            r = engine_client.get(
                f"{engine_client.base_url}/api/v2/inferences/query",
                params={
                    'task_id': task_id,
                    'sort': 'desc',
                    'page_size': 25,
                    'page': page
                },
                verify=False
            )
            r.raise_for_status()
            result = r.json()
            inferences = result["inferences"]
            if len(inferences) == 0:
                break
            all_inferences.extend(inferences)
            page+=1
        except Exception as e:
            print(e)
            break
    return all_inferences


if __name__ == "__main__":
    create_api_key()

    pii_rule = {
    "name": "Test PII Rule",
    "type": "PIIDataRule",
    "apply_to_prompt": True,
    "apply_to_response": False,
    "config": {
        "disabled_pii_entities": [
        "CRYPTO",
        "DATE_TIME",
        "CREDIT_CARD",
        "IBAN_CODE",
        "IP_ADDRESS",
        "NRP",
        "LOCATION",
        "PERSON",
        "MEDICAL_LICENSE",
        "US_BANK_NUMBER",
        "US_DRIVER_LICENSE",
        "US_ITIN",
        "US_PASSPORT"
        ]}
    }
    prompt_injection_rule = {
    "name": "Test Prompt Injection Rule",
    "type": "PromptInjectionRule",
    "apply_to_prompt": True,
    "apply_to_response": False
    }

    task_created = False
    if not TASK_ID:
        engine_client = get_engine_client()
        task = create_task("Test Task")
        TASK_ID = task["id"]
        print(f"Created Task: {TASK_ID}")

        create_task_rule(TASK_ID, pii_rule)
        create_task_rule(TASK_ID, prompt_injection_rule)
        task_created = True

    print(f"Task Definition: {get_task(TASK_ID)}")

    if not task_created:
        # Query last 24 hours of inferences
        inferences = query_inferences(TASK_ID)
        print(f"\nInferences:")
        for inference in inferences:
            print(f"Inference ID: {inference['id']}")
            print(f"Input: {inference['inference_prompt']['message']}")
            failed = False
            failed_rules = []
            if inference.get('result') == 'Fail':
                failed = True
                # Look for failed rules in inference_prompt.prompt_rule_results
                if inference.get('inference_prompt') and inference['inference_prompt'].get('prompt_rule_results'):
                    for rule in inference['inference_prompt']['prompt_rule_results']:
                        if rule['result'] == 'Fail':
                            failed_rules.append(rule['name'])
            print(f"Failed: {failed}")
            if failed:
                print(f"Failed Rules: {', '.join(failed_rules)}")
            print("---")
