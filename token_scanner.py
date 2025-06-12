import requests
import time

HELIUS_API_KEY = "3e8a19ae-51ac-4003-b2c2-595cbfccec86"
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"

DEPLOYER_ADDRESSES = [
    "8VAHbXp4X5zGxB6M7HfGxnwZJ6K88ewzYkD5YPb8tuW9",  # Example
    "BELIEVEDEPLOYERADDRESSHERE"
]

TX_LIMIT = 10

def fetch_new_tokens():
    new_tokens = []

    for deployer in DEPLOYER_ADDRESSES:
        body = {
            "jsonrpc": "2.0",
            "id": "scan",
            "method": "getSignaturesForAddress",
            "params": [
                deployer,
                {"limit": TX_LIMIT}
            ]
        }

        try:
            response = requests.post(HELIUS_RPC_URL, json=body)
            response.raise_for_status()
            result = response.json().get("result", [])

            for tx in result:
                signature = tx["signature"]
                token_data = analyze_signature(signature)
                if token_data:
                    new_tokens.append(token_data)

        except Exception as e:
            print(f"[ERROR] Fetch/analyze failed for {deployer}: {e}")

    return new_tokens

def analyze_signature(signature):
    body = {
        "jsonrpc": "2.0",
        "id": "parse",
        "method": "getParsedTransaction",
        "params": [
            signature,
            {"maxSupportedTransactionVersion": 0}
        ]
    }

    try:
        response = requests.post(HELIUS_RPC_URL, json=body)
        response.raise_for_status()
        tx_data = response.json().get("result", {})
        if not tx_data:
            return None

        instructions = tx_data.get("transaction", {}).get("message", {}).get("instructions", [])
        for ix in instructions:
            program = ix.get("program", "")
            parsed = ix.get("parsed", {})

            if program == "spl-token" and parsed.get("type") == "initializeMint":
                mint = parsed.get("info", {}).get("mint")
                decimals = parsed.get("info", {}).get("decimals", 0)
                return {
                    "mint": mint,
                    "signature": signature,
                    "decimals": decimals
                }

    except Exception as e:
        print(f"[ERROR] Failed to parse tx {signature}: {e}")

    return None

# ✅ Added run_scanner for main.py
def run_scanner(callback):
    while True:
        tokens = fetch_new_tokens()
        for token in tokens:
            callback(token)
        time.sleep(30)
