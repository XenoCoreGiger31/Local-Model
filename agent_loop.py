import requests
import json
import logging
import re
import os
from datetime import datetime

# ============================================================
# 🚀 LOGGING SETUP - Human Readable Session Logs
# ============================================================

LOG_DIR = "/home/bigkali/security-agent/logs"
os.makedirs(LOG_DIR, exist_ok=True)

SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"{LOG_DIR}/session_{SESSION_ID}.log"

class EmojiFormatter(logging.Formatter):
    ICONS = {
        "SCAN":    "🔍",
        "ATTACK":  "⚔️ ",
        "SUCCESS": "🎉😄",
        "FAIL":    "😤💀",
        "ERROR":   "😭🔥",
        "TOOL":    "✅👍",
        "MEMORY":  "🧠",
        "MODEL":   "🤖",
        "CHAIN":   "🔗",
        "REPORT":  "📝",
        "ENGAGE":  "💣",
        "GOAL":    "🎯",
        "START":   "🚀",
        "FILE":    "📁",
        "WEB":     "🌐",
        "CREDS":   "🔑",
    }

    def format(self, record):
        time = datetime.now().strftime("%H:%M:%S")
        msg = record.getMessage()
        icon = "ℹ️ "
        for key, emoji in self.ICONS.items():
            if f"[{key}]" in msg:
                icon = emoji
                msg = msg.replace(f"[{key}]", "").strip()
                break
        if record.levelno == logging.WARNING:
            icon = "😤💀"
        if record.levelno == logging.ERROR:
            icon = "😭🔥"
        return f"[{time}] {icon}  {msg}"

def setup_logger():
    logger = logging.getLogger("agent")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    fmt = EmojiFormatter()
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

log = setup_logger()
log.info(f"[START] SECURITY AGENT SESSION {SESSION_ID}")
log.info(f"[FILE] Log file: {LOG_FILE}")

# ============================================================
# ⚙️  CONFIG
# ============================================================

OLLAMA_URL = "http://192.168.0.39:1234/v1/chat/completions"
MCP_URL = "http://localhost:8000"

SYSTEM_PROMPT = """You are an autonomous penetration testing agent.

AVAILABLE TOOLS:
- run_masscan: Fast port scanner
- run_nmap: Detailed port scanner
- run_sqlmap: SQL injection testing (params: target, level, risk)
- run_nikto: Web vulnerability scanner
- run_hydra: Credential brute forcing (params: target, service, username, wordlist)
- run_searchsploit: Find exploits
- run_command: Execute any shell command
- write_file: Write content to files
- read_file: Read file contents
- run_john: Hash cracking (needs hash_file param)
- run_gobuster: Web directory brute forcing
- run_enum4linux: SMB/Samba enumeration (params: target)
- run_medusa: Fast credential brute forcing
- run_ncrack: Network authentication cracking (params: target, service, wordlist)

HYDRA SERVICE NAMES - use EXACTLY these:
- FTP: "ftp"
- SSH: "ssh"
- Telnet: "telnet" — SKIP telnet brute force, too slow, low value
- MySQL: "mysql"
- VNC: "vnc"
- PostgreSQL: "postgres"
- SMB: "smb"
- HTTP: "http-get"

HYDRA WORDLISTS - use these in order of speed:
- Fast: "/usr/share/seclists/Passwords/Common-Credentials/top-20-common-SSH-passwords.txt"
- Medium: "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"
- Full: "/usr/share/wordlists/rockyou.txt" — ONLY use if fast and medium lists fail, and only for high-value services like SSH and FTP. NEVER use on telnet or slow protocols.

SEARCHSPLOIT: always use "keyword" param with service name only e.g. "vsftpd 2.3.4"

RESPONSE FORMAT - VALID JSON ONLY:
{"chain": [{"tool": "tool_name", "param1": "value1"}]}

NO explanations. NO markdown. ONLY JSON."""


# ============================================================
# 🤖 MODEL + TOOL EXECUTION
# ============================================================


class AgentMemory:
    def __init__(self):
        self.open_ports = []
        self.tried_ports = []
        self.successful_attacks = []
        self.failed_attacks = []
        self.findings = []

    def add_ports(self, ports):
        for p in ports:
            if p not in self.open_ports:
                self.open_ports.append(p)
        log.info(f"[MEMORY] Open ports discovered: {self.open_ports}")

    def add_finding(self, port, tool, detail):
        self.findings.append({"port": port, "tool": tool, "detail": detail, "time": datetime.now().strftime("%H:%M:%S")})
        log.info(f"[SUCCESS] Port {port} → {tool}: {detail}")

    def next_untried_port(self):
        for p in self.open_ports:
            if p not in self.tried_ports:
                return p
        return None

    def mark_tried(self, port, success=False):
        if port not in self.tried_ports:
            self.tried_ports.append(port)
        if success:
            self.successful_attacks.append(port)
            log.info(f"[SUCCESS] Exploit landed on port {port}")
        else:
            self.failed_attacks.append(port)
            log.warning(f"[FAIL] Nothing worked on port {port}")

    def has_untried_ports(self):
        return any(p not in self.tried_ports for p in self.open_ports)

    def summary(self):
        return {"open_ports": self.open_ports, "tried": self.tried_ports, "successes": self.successful_attacks, "failures": self.failed_attacks, "findings": self.findings}

def parse_model_response(raw):
    try:
        cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found")
        return json.loads(cleaned[start:end])
    except Exception as e:
        log.error(f"[ERROR] JSON parse failed: {e}")
        return {"chain": []}

def call_model(goal):
    log.info(f"[MODEL] Thinking about: {goal[:80]}...")
    payload = {
        "model": "qwen2.5-14b-instruct-abliterated-abliterated",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": goal}
        ],
        "temperature": 0.1,
        "top_p": 0.9
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=7200)
        raw = response.json()["choices"][0]["message"]["content"]
        log.info(f"[MODEL] Response received ✅👍")
        return parse_model_response(raw)
    except Exception as e:
        log.error(f"[ERROR] Model call failed: {e}")
        return {"chain": []}

def extract_ports(output):
    ports = re.findall(r'(\d+)/tcp\s+open|(\d+)/udp\s+open|port\s+(\d+)|open port (\d+)', output, re.IGNORECASE)
    found = []
    for match in ports:
        port = next(p for p in match if p)
        if port not in found:
            found.append(port)
    return found

def execute_step(step):
    tool = step.get("tool", "unknown")
    start_time = datetime.now()
    log.info(f"[TOOL] Running → {tool} | params: { {k:v for k,v in step.items() if k != 'tool'} }")
    try:
        result = requests.post(MCP_URL, json=step, timeout=7200)
        result_data = result.json()
        output = result_data.get("stdout", "")
        status = result_data.get("status", "")
        duration = (datetime.now() - start_time).seconds
        if status == "success":
            log.info(f"[TOOL] ✅👍 {tool} completed in {duration}s")
            if output:
                log.info(f"[TOOL] Output preview: {output[:200]}")
        else:
            log.warning(f"[FAIL] 😤💀 {tool} failed after {duration}s → {result_data.get('message', 'unknown error')}")
        return output, status == "success"
    except Exception as e:
        log.error(f"[ERROR] 😭🔥 {tool} exception: {e}")
        return "", False

# ============================================================
# 🔍 RECON + ⚔️  ATTACK
# ============================================================

def run_recon(target, memory):
    log.info(f"[SCAN] Starting recon on {target}")
    goal = f"Scan {target} with masscan then nmap to find all open ports and services. JSON only."
    data = call_model(goal)
    for step in data.get("chain", []):
        output, ok = execute_step(step)
        if output:
            ports = extract_ports(output)
            if ports:
                memory.add_ports(ports)
                log.info(f"[SCAN] 🎉😄 Found {len(ports)} open ports: {ports}")
            else:
                log.warning(f"[SCAN] 😤💀 No ports found in output")

def run_attack_loop(target, memory):
    log.info(f"[ATTACK] Starting attack loop on {target}")
    while memory.has_untried_ports():
        port = memory.next_untried_port()
        log.info(f"[ATTACK] ⚔️  Targeting port {port}")
        goal = f"Target: {target} Port: {port}. Failed ports: {memory.failed_attacks}. Exploit this port with any available tool. Try multiple tools if needed. JSON only."
        data = call_model(goal)
        chain = data.get("chain", [])
        if not chain:
            log.warning(f"[FAIL] 😤💀 No attack chain generated for port {port}")
            memory.mark_tried(port, success=False)
            continue
        success = False
        for step in chain:
            output, ok = execute_step(step)
            if ok and output and any(x in output.lower() for x in ["password", "login", "session", "shell", "success", "found", "valid"]):
                success = True
                memory.add_finding(port, step.get("tool"), output[:2000])
        memory.mark_tried(port, success=success)
    log.info(f"[ATTACK] Attack loop complete")
    summary = memory.summary()
    log.info(f"[MEMORY] Final summary: {summary}")
    if memory.successful_attacks:
        log.info(f"[SUCCESS] 🎉😄 BREACHED ports: {memory.successful_attacks}")
    else:
        log.warning(f"[FAIL] 😤💀 No successful breaches this session")

def run_full_engagement(target):
    memory = AgentMemory()
    log.info(f"[ENGAGE] 💣 Full engagement started on {target}")
    run_recon(target, memory)
    if memory.open_ports:
        run_attack_loop(target, memory)
    else:
        log.warning(f"[FAIL] 😤💀 No open ports found — aborting engagement")
    return memory

# ============================================================
# 🎯 MAIN
# ============================================================

def execute_chain(chain):
    for i, step in enumerate(chain, 1):
        log.info(f"[CHAIN] 🔗 Step {i} of {len(chain)}: {step.get('tool')}")
        execute_step(step)

def main():
    log.info("[START] 🚀 AUTONOMOUS SECURITY AGENT ONLINE")
    print("=" * 60)
    print("⚔️   AUTONOMOUS SECURITY AGENT")
    print("=" * 60)
    print("Commands:")
    print("  engage <target>  - full recon + attack loop")
    print("  <any goal>       - single model query")
    print("  exit             - quit")
    print(f"  📝 Session log: {LOG_FILE}")
    print("=" * 60)

    while True:
        try:
            goal = input(">>> ").strip()
            if goal.lower() == "exit":
                log.info("[START] Agent shutdown. Goodbye! 👋")

                break
            if not goal:
                continue
            log.info(f"[GOAL] 🎯 {goal}")
            if goal.startswith("engage "):
                target = goal.replace("engage ", "").strip()
                memory = run_full_engagement(target)
                log.info(f"[REPORT] 📝 Engagement complete — run report generator for client memo")
            else:
                data = call_model(goal)
                chain = data.get("chain", [])
                if chain:
                    execute_chain(chain)
                else:
                    log.warning("[FAIL] 😤💀 No tool chain generated")
        except KeyboardInterrupt:
            log.info("[START] Interrupted by user")
            import subprocess
            subprocess.run(["python3", "/home/bigkali/security-agent/report_generator.py", LOG_FILE])
            break
        except Exception as e:
            log.error(f"[ERROR] 😭🔥 Fatal error: {e}")
            break

if __name__ == "__main__":
    main()

# ============================================================
# 🧠 AGENT MEMORY
# ============================================================

