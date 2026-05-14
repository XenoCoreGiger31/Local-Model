import requests
import json

OLLAMA_URL = "http://192.168.0.39:1234/v1/chat/completions"
MCP_URL = "http://localhost:8000"
MODEL_NAME = "qwen"

def call_model(goal):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": (
                    "Generate ONLY JSON. Valid tools: run_command, run_masscan, run_nmap, write_file, read_file.\n"
                    "Example: {\"chain\": [{\"tool\": \"run_masscan\", \"target\": \"192.168.1.100\", \"ports\": \"1-443\"}]}\n"
                    "Goal: " + goal
                )
            }
        ],
        "temperature": 0.05
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        content = response.json()["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing: {e}")
        return {"chain": []}

def execute_chain(chain):
    print("\nEXECUTING:\n")
    for i, step in enumerate(chain, 1):
        print(f"{i}. {step}")
        try:
            result = requests.post(MCP_URL, json=step, timeout=30)
            print(f"Result: {result.json()}\n")
        except Exception as e:
            print(f"Error: {e}\n")

def main():
    print("INTELLIGENT SECURITY AGENT\n")
    while True:
        goal = input("Goal: ").strip()
        if goal.lower() == "exit":
            break
        if not goal:
            continue
        
        data = call_model(goal)
        chain = data.get("chain", [])
        
        if chain:
            print(f"\nChain: {chain}")
            execute_chain(chain)
        else:
            print("No chain generated")

if __name__ == "__main__":
    main()
