# config/secret_manager.py
import os
import sys
import time
import threading
import hvac
from dotenv import load_dotenv

load_dotenv()

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
SECRET_PATH = "ai-research-agent"

current_secrets = {}
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

def fetch_secrets() -> dict:
    if not client.is_authenticated():
        raise Exception("Vault authentication failed!")
    response = client.secrets.kv.v2.read_secret_version(
        path=SECRET_PATH,
        mount_point="secret"
    )
    return response['data']['data']

def get_flag(key: str) -> bool:
    return current_secrets.get(key, "false").lower() == "true"

def get_secret(key: str) -> str:
    return current_secrets.get(key, "")

def handle_change(key: str, old_value: str, new_value: str):
    critical_secrets = [
        "MONGODB_URL", "DATABASE_NAME", "SECRET_KEY",
        "GOOGLE_API_KEY", "GROQ_API_KEY", "TAVILY_API_KEY"
    ]
    if key in critical_secrets:
        print(f"🔴 Critical secret '{key}' changed! Crashing...")
        sys.exit(1)

    if key == "TAVILY_SEARCH_ENABLED":
        if new_value.lower() == "true":
            print("✅ Tavily Search ENABLED")
        else:
            print("🔴 Tavily Search DISABLED")

def watch_secrets():
    global current_secrets
    while True:
        time.sleep(30)
        try:
            new_secrets = fetch_secrets()
            for key, new_value in new_secrets.items():
                old_value = current_secrets.get(key)
                if old_value is not None and old_value != new_value:
                    print(f"🔄 '{key}' changed: {old_value} → {new_value}")
                    current_secrets[key] = new_value
                    os.environ[key] = new_value
                    handle_change(key, old_value, new_value)
        except Exception as e:
            print(f"⚠️ Watch error: {e}")

def load_secrets():
    global current_secrets
    print("🔐 Loading secrets from HashiCorp Vault...")
    if not client.is_authenticated():
        raise Exception("❌ Vault authentication failed!")
    current_secrets = fetch_secrets()
    for key, value in current_secrets.items():
        os.environ[key] = value
    print(f"✅ {len(current_secrets)} secrets loaded from Vault!")
    print(f"📊 TAVILY_SEARCH_ENABLED: {get_flag('TAVILY_SEARCH_ENABLED')}")
    thread = threading.Thread(target=watch_secrets, daemon=True)
    thread.start()
    print("👀 Vault watcher started — checking every 30 seconds")