#!/usr/bin/env python3
"""
MCP SERVER - Autonomous Tool Execution Engine
Hardened: token auth, no shell=True, no auto-sudo, input validation.
"""

import subprocess
import json
import sys
import os
import re
import secrets
import shutil
from datetime import datetime
from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

LOG_DIR = os.environ.get("MCP_LOG_DIR", os.path.join(os.path.expanduser("~"), "mcp-logs"))
os.makedirs(LOG_DIR, exist_ok=True)
SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"mcp_{SESSION_ID}.log")

AUTH_TOKEN = os.environ.get("MCP_AUTH_TOKEN")
if not AUTH_TOKEN:
    AUTH_TOKEN = secrets.token_hex(32)
    print(f"\n{'='*60}")
    print("  NO MCP_AUTH_TOKEN set — generated ephemeral token:")
    print(f"  {AUTH_TOKEN}")
    print(f"  Export MCP_AUTH_TOKEN to use a persistent token.")
    print(f"{'='*60}\n")

ALLOWED_TOOLS = {
    "run_nmap", "run_masscan", "run_netstat", "run_sqlmap", "run_nikto",
    "run_hydra", "run_searchsploit", "run_curl", "run_wget",
    "run_john", "run_ncrack", "run_gobuster", "run_enum4linux",
    "run_medusa", "run_subfinder", "run_nuclei", "run_katana",
    "run_ffuf", "run_httpx", "write_file", "read_file",
}

TIMEOUT = int(os.environ.get("MCP_TIMEOUT", "300"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

class EmojiFormatter(logging.Formatter):
    ICONS = {
        "TOOL": "->", "FAIL": "!!", "ERROR": "ERR",
        "START": ">>", "FILE": "F", "WEB": "W",
        "SCAN": "S", "SUCCESS": "OK",
    }
    def format(self, record):
        ts = datetime.now().strftime("%H:%M:%S")
        msg = record.getMessage()
        tag = "   "
        for key, icon in self.ICONS.items():
            if f"[{key}]" in msg:
                tag = icon
                msg = msg.replace(f"[{key}]", "").strip()
                break
        return f"[{ts}] {tag}  {msg}"

def setup_logger():
    lgr = logging.getLogger("mcp")
    lgr.setLevel(logging.DEBUG)
    lgr.handlers = []
    fmt = EmojiFormatter()
    fh = logging.FileHandler(LOG_FILE)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    lgr.addHandler(fh)
    lgr.addHandler(sh)
    return lgr

logger = setup_logger()

# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

_SAFE_TARGET = re.compile(r"^[a-zA-Z0-9.\-:/\[\]]+$")
_SAFE_FLAG = re.compile(r"^-{1,2}[a-zA-Z0-9][a-zA-Z0-9_\-=,.:/]*$")
_SAFE_PATH = re.compile(r"^[a-zA-Z0-9_./ \-]+$")

def _validate_target(value, label="target"):
    v = value.strip()
    if not v:
        return f"Empty {label}"
    if not _SAFE_TARGET.match(v):
        return f"Invalid characters in {label}: {v!r}"
    return None

def _validate_flags(value):
    for token in value.split():
        if not _SAFE_FLAG.match(token):
            return f"Invalid flag token: {token!r}"
    return None

def _validate_path(value):
    if not value.strip():
        return "Empty path"
    if not _SAFE_PATH.match(value.strip()):
        return f"Invalid path characters: {value!r}"
    if ".." in value:
        return f"Path traversal not allowed: {value!r}"
    return None

def _find_binary(name):
    return shutil.which(name)

def _run(argv, timeout=TIMEOUT):
    """Run a command as an argv list — never through a shell."""
    logger.info(f"[TOOL] exec: {argv}")
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return {"status": "success", "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        return {
            "status": "error",
            "error_type": "command_failed",
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except FileNotFoundError:
        return {"status": "error", "error_type": "command_not_found", "message": f"{argv[0]!r} not found on PATH"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "error_type": "timeout", "message": f"Timed out after {timeout}s"}
    except Exception as e:
        return {"status": "error", "error_type": "execution_error", "message": str(e)}

def _err(msg):
    return {"status": "error", "error_type": "invalid_params", "message": msg}

# ---------------------------------------------------------------------------
# Tool implementations — each returns a dict, never touches shell=True
# ---------------------------------------------------------------------------

def tool_run_nmap(params):
    target = params.get("target", "")
    flags = params.get("flags", "-sV")
    err = _validate_target(target)
    if err:
        return _err(err)
    err = _validate_flags(flags)
    if err:
        return _err(err)
    argv = ["nmap"] + flags.split() + [target]
    return _run(argv)

def tool_run_masscan(params):
    target = params.get("target", "")
    ports = params.get("ports", "1-65535")
    rate = params.get("rate", "1000")
    err = _validate_target(target)
    if err:
        return _err(err)
    if not re.match(r"^[\d,\- ]+$", str(ports)):
        return _err(f"Invalid ports: {ports!r}")
    if not re.match(r"^\d+$", str(rate)):
        return _err(f"Invalid rate: {rate!r}")
    argv = ["masscan", target, "-p", str(ports), "--rate", str(rate)]
    return _run(argv)

def tool_run_netstat(params):
    flags = params.get("flags", "-tuln")
    err = _validate_flags(flags)
    if err:
        return _err(err)
    result = _run(["netstat"] + flags.split())
    if result["status"] != "success":
        result2 = _run(["ss"] + flags.split())
        if result2["status"] == "success":
            result2["note"] = "Used 'ss' (modern netstat replacement)"
            return result2
    return result

def tool_run_sqlmap(params):
    target = params.get("target", "")
    technique = params.get("technique", "B")
    dbms = params.get("dbms", "")
    level = params.get("level", "1")
    risk = params.get("risk", "1")
    if not target:
        return _err("No target URL specified")
    if not re.match(r"^https?://", target):
        return _err("Target must be an http(s) URL")
    if not re.match(r"^[BEUSTQ]+$", str(technique)):
        return _err(f"Invalid technique: {technique!r}")
    if not re.match(r"^[1-5]$", str(level)):
        return _err(f"Invalid level: {level!r}")
    if not re.match(r"^[1-3]$", str(risk)):
        return _err(f"Invalid risk: {risk!r}")
    argv = ["sqlmap", "-u", target, f"--technique={technique}", f"--level={level}", f"--risk={risk}", "--batch"]
    if dbms:
        if not re.match(r"^[a-zA-Z0-9]+$", dbms):
            return _err(f"Invalid dbms: {dbms!r}")
        argv.append(f"--dbms={dbms}")
    return _run(argv, timeout=600)

def tool_run_nikto(params):
    target = params.get("target", "")
    port = params.get("port", "80")
    err = _validate_target(target)
    if err:
        return _err(err)
    if not re.match(r"^\d+$", str(port)):
        return _err(f"Invalid port: {port!r}")
    target = target.replace("http://", "").replace("https://", "").rstrip("/")
    argv = ["nikto", "-h", target, "-p", str(port), "-Format", "txt"]
    return _run(argv, timeout=600)

def tool_run_hydra(params):
    target = params.get("target", "")
    service = params.get("service", "ssh")
    username = params.get("username", "")
    wordlist = params.get("wordlist", "")
    threads = params.get("threads", "16")
    err = _validate_target(target)
    if err:
        return _err(err)
    if not re.match(r"^[a-z0-9\-]+$", service):
        return _err(f"Invalid service: {service!r}")
    if not username:
        return _err("No username specified")
    if not wordlist:
        return _err("No wordlist specified")
    err = _validate_path(wordlist)
    if err:
        return _err(err)
    if not re.match(r"^\d+$", str(threads)):
        return _err(f"Invalid threads: {threads!r}")
    argv = ["hydra", "-l", username, "-P", wordlist, "-t", str(threads), "-I", f"{service}://{target}"]
    return _run(argv, timeout=600)

def tool_run_searchsploit(params):
    keyword = params.get("keyword", "")
    type_filter = params.get("type", "")
    if not keyword or not re.match(r"^[a-zA-Z0-9 .\-_/]+$", keyword):
        return _err(f"Invalid keyword: {keyword!r}")
    argv = ["searchsploit", keyword]
    if type_filter:
        if not re.match(r"^[a-zA-Z]+$", type_filter):
            return _err(f"Invalid type filter: {type_filter!r}")
        argv += ["-t", type_filter]
    return _run(argv)

def tool_run_curl(params):
    url = params.get("url", "")
    method = params.get("method", "GET")
    headers = params.get("headers", "")
    data = params.get("data", "")
    if not url:
        return _err("No URL specified")
    if not re.match(r"^https?://", url):
        return _err("URL must start with http(s)://")
    if method not in ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"):
        return _err(f"Invalid HTTP method: {method!r}")
    argv = ["curl", "-X", method, url, "-v", "--max-time", "60"]
    if headers:
        for h in headers.split("\n"):
            h = h.strip()
            if h:
                argv += ["-H", h]
    if data and method in ("POST", "PUT", "PATCH"):
        argv += ["-d", data]
    return _run(argv)

def tool_run_wget(params):
    url = params.get("url", "")
    output = params.get("output", "")
    recursive = params.get("recursive", False)
    if not url:
        return _err("No URL specified")
    if not re.match(r"^https?://", url):
        return _err("URL must start with http(s)://")
    argv = ["wget", url, "--max-redirect=5", "--timeout=30"]
    if output:
        err = _validate_path(output)
        if err:
            return _err(err)
        argv += ["-O", output]
    if recursive:
        argv += ["-r", "--level=2"]
    return _run(argv)

def tool_run_john(params):
    hash_file = params.get("hash_file", "")
    wordlist = params.get("wordlist", "")
    fmt = params.get("format", "")
    if not hash_file:
        return _err("No hash file specified")
    err = _validate_path(hash_file)
    if err:
        return _err(err)
    argv = ["john", hash_file]
    if wordlist:
        err = _validate_path(wordlist)
        if err:
            return _err(err)
        argv.append(f"--wordlist={wordlist}")
    if fmt:
        if not re.match(r"^[a-zA-Z0-9\-]+$", fmt):
            return _err(f"Invalid format: {fmt!r}")
        argv.append(f"--format={fmt}")
    return _run(argv, timeout=600)

def tool_run_gobuster(params):
    target = params.get("target", "")
    wordlist = params.get("wordlist", "")
    mode = params.get("mode", "dir")
    err = _validate_target(target)
    if err:
        return _err(err)
    if mode not in ("dir", "dns", "vhost", "fuzz"):
        return _err(f"Invalid mode: {mode!r}")
    if not wordlist:
        wordlist = "/usr/share/seclists/Discovery/Web-Content/common.txt"
    err = _validate_path(wordlist)
    if err:
        return _err(err)
    argv = ["gobuster", mode, "-u", target, "-w", wordlist, "-t", "20"]
    return _run(argv, timeout=600)

def tool_run_enum4linux(params):
    target = params.get("target", "")
    err = _validate_target(target)
    if err:
        return _err(err)
    argv = ["enum4linux", "-a", target]
    return _run(argv)

def tool_run_medusa(params):
    target = params.get("target", "")
    service = params.get("service", "ssh")
    username = params.get("username", "")
    wordlist = params.get("wordlist", "")
    err = _validate_target(target)
    if err:
        return _err(err)
    if not username:
        return _err("No username specified")
    if not re.match(r"^[a-z0-9\-]+$", service):
        return _err(f"Invalid service: {service!r}")
    if not wordlist:
        wordlist = "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"
    err = _validate_path(wordlist)
    if err:
        return _err(err)
    argv = ["medusa", "-h", target, "-u", username, "-P", wordlist, "-M", service, "-t", "4"]
    return _run(argv)

def tool_run_ncrack(params):
    target = params.get("target", "")
    service = params.get("service", "ssh")
    users = params.get("users", "root,admin")
    wordlist = params.get("wordlist", "")
    err = _validate_target(target)
    if err:
        return _err(err)
    if not re.match(r"^[a-z0-9\-]+$", service):
        return _err(f"Invalid service: {service!r}")
    if not re.match(r"^[a-zA-Z0-9,_\-]+$", users):
        return _err(f"Invalid users list: {users!r}")
    if not wordlist:
        wordlist = "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"
    err = _validate_path(wordlist)
    if err:
        return _err(err)
    user_list = users.split(",")
    argv = ["ncrack", f"{service}://{target}"]
    for u in user_list:
        argv += ["--user", u]
    argv += ["-P", wordlist]
    return _run(argv, timeout=600)

def tool_run_subfinder(params):
    domain = params.get("domain", "")
    silent = params.get("silent", True)
    if not domain or not re.match(r"^[a-zA-Z0-9.\-]+$", domain):
        return _err(f"Invalid domain: {domain!r}")
    argv = ["subfinder", "-d", domain]
    if silent:
        argv.append("-silent")
    return _run(argv)

def tool_run_nuclei(params):
    target = params.get("target", "")
    templates = params.get("templates", "")
    severity = params.get("severity", "")
    if not target:
        return _err("No target specified")
    argv = ["nuclei", "-u", target]
    if templates:
        err = _validate_path(templates)
        if err:
            return _err(err)
        argv += ["-t", templates]
    if severity:
        if not re.match(r"^(info|low|medium|high|critical)(,(info|low|medium|high|critical))*$", severity):
            return _err(f"Invalid severity: {severity!r}")
        argv += ["-severity", severity]
    argv.append("-silent")
    return _run(argv, timeout=600)

def tool_run_katana(params):
    target = params.get("target", "")
    depth = params.get("depth", "3")
    if not target:
        return _err("No target specified")
    if not re.match(r"^[1-9]\d?$", str(depth)):
        return _err(f"Invalid depth: {depth!r}")
    argv = ["katana", "-u", target, "-depth", str(depth), "-silent"]
    return _run(argv)

def tool_run_ffuf(params):
    url = params.get("url", "")
    wordlist = params.get("wordlist", "")
    param = params.get("param", "FUZZ")
    if not url:
        return _err("No URL specified")
    if not wordlist:
        wordlist = "/usr/share/seclists/Discovery/Web-Content/common.txt"
    err = _validate_path(wordlist)
    if err:
        return _err(err)
    if param not in url:
        url = url.rstrip("/") + f"/{param}"
    argv = ["ffuf", "-u", url, "-w", wordlist, "-mc", "200,301,302,403", "-silent"]
    return _run(argv)

def tool_run_httpx(params):
    target = params.get("target", "")
    flags = params.get("flags", "")
    if not target:
        return _err("No target specified")
    binary = _find_binary("httpx")
    if not binary:
        return _err("httpx not found on PATH")
    argv = [binary, "-u", target]
    if flags:
        err = _validate_flags(flags)
        if err:
            return _err(err)
        argv += flags.split()
    else:
        argv += ["-status-code", "-title", "-tech-detect", "-silent"]
    return _run(argv)

def tool_write_file(params):
    filename = params.get("filename", "")
    content = params.get("content", "")
    err = _validate_path(filename)
    if err:
        return _err(err)
    try:
        with open(filename, "w") as f:
            f.write(content)
        return {"status": "success", "message": f"Written to {filename}", "bytes_written": len(content)}
    except Exception as e:
        return {"status": "error", "error_type": "file_write_error", "message": str(e)}

def tool_read_file(params):
    filename = params.get("filename", "")
    err = _validate_path(filename)
    if err:
        return _err(err)
    try:
        with open(filename, "r") as f:
            content = f.read(10 * 1024 * 1024)
        return {"status": "success", "filename": filename, "content": content, "bytes_read": len(content)}
    except FileNotFoundError:
        return {"status": "error", "error_type": "file_not_found", "message": f"Not found: {filename}"}
    except Exception as e:
        return {"status": "error", "error_type": "file_read_error", "message": str(e)}

TOOL_DISPATCH = {
    "run_nmap": tool_run_nmap,
    "run_masscan": tool_run_masscan,
    "run_netstat": tool_run_netstat,
    "run_sqlmap": tool_run_sqlmap,
    "run_nikto": tool_run_nikto,
    "run_hydra": tool_run_hydra,
    "run_searchsploit": tool_run_searchsploit,
    "run_curl": tool_run_curl,
    "run_wget": tool_run_wget,
    "run_john": tool_run_john,
    "run_gobuster": tool_run_gobuster,
    "run_enum4linux": tool_run_enum4linux,
    "run_medusa": tool_run_medusa,
    "run_ncrack": tool_run_ncrack,
    "run_subfinder": tool_run_subfinder,
    "run_nuclei": tool_run_nuclei,
    "run_katana": tool_run_katana,
    "run_ffuf": tool_run_ffuf,
    "run_httpx": tool_run_httpx,
    "write_file": tool_write_file,
    "read_file": tool_read_file,
}

# ---------------------------------------------------------------------------
# Auth middleware
# ---------------------------------------------------------------------------

def _check_auth():
    token = request.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token[7:]
    if not secrets.compare_digest(token, AUTH_TOKEN):
        return "Invalid or missing auth token"
    return None

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["POST"])
def execute():
    err = _check_auth()
    if err:
        return jsonify({"status": "error", "error_type": "auth_error", "message": err}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "error_type": "invalid_request", "message": "No JSON data provided"}), 400

        tool = data.get("tool")
        if not tool:
            return jsonify({"status": "error", "error_type": "missing_tool", "message": "No 'tool' parameter specified"}), 400

        if tool not in ALLOWED_TOOLS:
            return jsonify({
                "status": "error",
                "error_type": "unsupported_tool",
                "message": f"Tool '{tool}' not supported",
                "available": sorted(ALLOWED_TOOLS),
            }), 400

        params = {k: v for k, v in data.items() if k != "tool"}
        handler = TOOL_DISPATCH[tool]
        result = handler(params)
        logger.info(f"[TOOL] {tool} -> {result.get('status', 'unknown')}")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"[ERROR] Server error: {e}")
        return jsonify({"status": "error", "error_type": "server_error", "message": str(e)}), 500

@app.route("/status", methods=["GET"])
def status():
    err = _check_auth()
    if err:
        return jsonify({"status": "error", "error_type": "auth_error", "message": err}), 401
    return jsonify({"status": "running", "supported_tools": sorted(ALLOWED_TOOLS)}), 200

if __name__ == "__main__":
    print("=" * 60)
    print("  MCP SERVER - HARDENED TOOL EXECUTION ENGINE")
    print("=" * 60)
    print(f"  Tools : {len(ALLOWED_TOOLS)}")
    print(f"  Bind  : localhost:8000 (loopback only)")
    print(f"  Auth  : Bearer token required (Authorization header)")
    print(f"  Shell : DISABLED (all commands run as argv lists)")
    print(f"  Sudo  : DISABLED (no auto-escalation)")
    print(f"  Log   : {LOG_FILE}")
    print("=" * 60)

    app.run(host="localhost", port=8000, debug=False)
