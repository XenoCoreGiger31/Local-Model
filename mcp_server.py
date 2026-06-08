#!/usr/bin/env python3
"""
MCP SERVER - Autonomous Tool Execution Engine
Executes security tools with intelligent error recovery and permission handling
"""

import subprocess
import json
import sys
from flask import Flask, request, jsonify
import logging


# SYSTEM PROMPT - Penetration Testing Agent
SYSTEM_PROMPT = """You are an autonomous penetration testing agent.
Understand context and user intent. Infer tools needed without asking.
Chain tools intelligently. Return ONLY final results - no tool chain narration."""

app = Flask(__name__)
import os
from datetime import datetime

LOG_DIR = "/home/bigkali/security-agent/logs"
os.makedirs(LOG_DIR, exist_ok=True)
SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"{LOG_DIR}/mcp_{SESSION_ID}.log"

class EmojiFormatter(logging.Formatter):
    ICONS = {
        "TOOL":    "✅👍",
        "FAIL":    "😤💀",
        "ERROR":   "😭🔥",
        "START":   "🚀",
        "FILE":    "📁",
        "WEB":     "🌐",
        "CREDS":   "🔑",
        "SCAN":    "🔍",
        "SUCCESS": "🎉😄",
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
    logger = logging.getLogger("mcp")
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

logging.basicConfig(level=logging.INFO)
logger = setup_logger()

# Supported tools
SUPPORTED_TOOLS = [
    "run_command", "run_masscan", "run_nmap", "run_netstat",
    "run_sqlmap", "run_nikto", "run_hydra", "run_searchsploit",
    "run_curl", "run_wget", "write_file", "read_file",
    "run_john", "run_ncrack", "run_gobuster", "run_enum4linux", "run_medusa"
]

# Kali tools that may need sudo
PRIVILEGED_TOOLS = {
    "masscan", "nmap", "arp-scan", "wireshark", "tcpdump",
    "iptables", "ip6tables", "ufw", "hashcat", "airmon-ng",
    "aircrack-ng", "hydra", "metasploit", "burpsuite"
}

class ToolExecutor:
    """Executes tools with intelligent error recovery and permission handling"""
    
    def __init__(self):
        self.execution_log = []
        self.error_recovery_attempts = {}
    
    def execute_tool(self, tool, params):
        """Execute a tool with automatic error recovery"""
        # Use system prompt to guide autonomous execution
        # No tool chain logging - only return final results
        
        if tool == "run_command":
            return self._run_command(params.get("command", ""))
        
        elif tool == "run_masscan":
            return self._run_masscan(
                params.get("target", ""),
                params.get("ports", "1-65535"),
                params.get("rate", "1000")
            )
        
        elif tool == "run_nmap":
            return self._run_nmap(
                params.get("target", ""),
                params.get("flags", "-sV")
            )
        
        elif tool == "run_netstat":
            return self._run_netstat(params.get("flags", "-tuln"))
        
        elif tool == "run_sqlmap":
            return self._run_sqlmap(
                params.get("target", ""),
                params.get("technique", "B"),
                params.get("dbms", ""),
                params.get("level", "1"),
                params.get("risk", "1")
            )
        
        elif tool == "run_nikto":
            return self._run_nikto(
                params.get("target", ""),
                params.get("port", "80"),
                params.get("ssl", False)
            )
        
        elif tool == "run_hydra":
            return self._run_hydra(
                params.get("target", ""),
                params.get("service", "ssh"),
                params.get("username", ""),
                params.get("wordlist", "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"),
                params.get("threads", "16")
            )
        
        elif tool == "run_searchsploit":
            return self._run_searchsploit(
                params.get("keyword", ""),
                params.get("type", "")
            )
        
        elif tool == "run_curl":
            return self._run_curl(
                params.get("url", ""),
                params.get("method", "GET"),
                params.get("headers", ""),
                params.get("data", "")
            )
        
        elif tool == "run_wget":
            return self._run_wget(
                params.get("url", ""),
                params.get("output", ""),
                params.get("recursive", False)
            )
        
        elif tool == "write_file":
            return self._write_file(
                params.get("filename", ""),
                params.get("content", "")
            )
        
        elif tool == "read_file":
            return self._read_file(params.get("filename", ""))
        elif tool == "run_john":
            return self._run_john(params.get("hash_file", ""), params.get("wordlist", ""), params.get("format", ""))

        elif tool == "run_ncrack":
            return self._run_ncrack(params.get("target", ""), params.get("service", "ssh"), params.get("users", ""), params.get("wordlist", ""))

        elif tool == "run_gobuster":
            return self._run_gobuster(params.get("target", ""), params.get("wordlist", ""), params.get("mode", "dir"))

        elif tool == "run_enum4linux":
            return self._run_enum4linux(params.get("target", ""))

        elif tool == "run_medusa":
            return self._run_medusa(params.get("target", ""), params.get("service", "ssh"), params.get("username", ""), params.get("wordlist", ""))

        else:
            return {
                "status": "error",
                "error_type": "unsupported_tool",
                "message": f"Tool '{tool}' not supported",
                "recovery_suggestion": f"Use one of: {', '.join(SUPPORTED_TOOLS)}"
            }
    
    def _execute_command(self, command, retry_with_sudo=False):
        """Execute shell command with intelligent error handling"""
        
        if retry_with_sudo and not command.strip().startswith("sudo"):
            command = f"sudo {command}"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=7200
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip()
                }
            
            else:
                # Intelligent error detection
                stderr = result.stderr.lower()
                stdout = result.stdout.lower()
                
                # Permission denied error
                if "permission denied" in stderr or "operation not permitted" in stderr:
                    if not retry_with_sudo:
                        # Auto-retry with sudo
                        return self._execute_command(command, retry_with_sudo=True)
                    else:
                        return {
                            "status": "error",
                            "error_type": "permission_denied",
                            "message": result.stderr,
                            "recovery_suggestion": "Check if tool is installed or try with elevated privileges"
                        }
                
                # Command not found
                elif "not found" in stderr or "command not found" in stderr:
                    return {
                        "status": "error",
                        "error_type": "command_not_found",
                        "message": result.stderr,
                        "recovery_suggestion": f"Install the tool or check spelling. Command was: {command}"
                    }
                
                # Timeout or resource issues
                elif "timed out" in stderr or "timeout" in stderr:
                    return {
                        "status": "error",
                        "error_type": "timeout",
                        "message": "Command execution timed out",
                        "recovery_suggestion": "Reduce scan scope or increase timeout"
                    }
                
                # Generic command failure
                else:
                    return {
                        "status": "error",
                        "error_type": "command_failed",
                        "message": result.stderr if result.stderr else result.stdout,
                        "recovery_suggestion": "Check command syntax and parameters"
                    }
        
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error_type": "timeout",
                "message": "Command execution timed out (600s)",
                "recovery_suggestion": "Reduce scan scope or increase timeout"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error_type": "execution_error",
                "message": str(e),
                "recovery_suggestion": "Check command syntax and ensure tool is installed"
            }
    
    def _run_command(self, command):
        """Execute arbitrary command"""
        if not command:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No command provided"
            }
        
        result = self._execute_command(command)
        return result
    
    def _run_masscan(self, target, ports, rate):
        """Execute masscan with intelligent error recovery"""
        if not target:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No target specified for masscan"
            }
        
        command = f"masscan {target} -p {ports} --rate {rate}"
        result = self._execute_command(command)
        
        if result["status"] != "success":
            # If masscan fails, try with sudo
            if "permission" in result.get("message", "").lower():
                result = self._execute_command(command, retry_with_sudo=True)
        
        return result
    
    def _run_nmap(self, target, flags):
        """Execute nmap with intelligent error recovery"""
        if not target:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No target specified for nmap"
            }
        
        command = f"nmap {flags} {target}"
        result = self._execute_command(command)
        
        if result["status"] != "success":
            # If nmap fails, try with sudo
            if "permission" in result.get("message", "").lower():
                result = self._execute_command(command, retry_with_sudo=True)
        
        return result
    
    def _run_netstat(self, flags):
        """Execute netstat"""
        command = f"netstat {flags}"
        result = self._execute_command(command)
        
        if result["status"] != "success":
            # Try ss as fallback (modern replacement for netstat)
            ss_command = f"ss {flags}"
            result = self._execute_command(ss_command)
            if result["status"] == "success":
                result["note"] = "Used 'ss' (modern netstat replacement)"
        
        return result
    
    def _run_sqlmap(self, target, technique, dbms, level, risk):
        """Execute sqlmap for SQL injection testing"""
        if not target:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No target URL specified for sqlmap"
            }
        
        command = f"sqlmap -u {target} --technique={technique} --level={level} --risk={risk}"
        
        if dbms:
            command += f" --dbms={dbms}"
        
        command += " --batch"  # Non-interactive mode
        
        result = self._execute_command(command)
        return result
    
    def _run_nikto(self, target, port, ssl):
        """Execute nikto for web vulnerability scanning"""
        if not target:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No target specified for nikto"
            }
        
        protocol = "https" if ssl else "http"
        command = f"nikto -h {protocol}://{target}:{port} -Format txt"
        
        result = self._execute_command(command)
        return result
    
    def _run_hydra(self, target, service, username, wordlist, threads):
        """Execute hydra for credential testing"""
        if not target or not service or not username or not wordlist:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "Missing parameters: target, service, username, and wordlist are required"
            }
        
        if service.lower() in ["vnc", "rdp"]:
            command = f"hydra -P {wordlist} -t 4 -I {service}://{target}"
        else:
            command = f"hydra -l {username} -P {wordlist} -t {threads} -I {service}://{target}"
        
        result = self._execute_command(command)
        return result
    
    def _run_searchsploit(self, keyword, type_filter):
        """Execute searchsploit for vulnerability lookup"""
        if not keyword:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No keyword specified for searchsploit"
            }
        
        command = f"searchsploit {keyword}"
        
        if type_filter:
            command += f" -t {type_filter}"
        
        result = self._execute_command(command)
        return result
    
    def _run_curl(self, url, method, headers, data):
        """Execute curl for web interaction"""
        if not url:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No URL specified for curl"
            }
        
        command = f"curl -X {method} \"{url}\""
        
        if headers:
            command += f" -H \"{headers}\""
        
        if data and method in ["POST", "PUT", "PATCH"]:
            command += f" -d '{data}'"
        
        command += " -v"  # Verbose output
        
        result = self._execute_command(command)
        return result
    
    def _run_wget(self, url, output, recursive):
        """Execute wget for file downloading"""
        if not url:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No URL specified for wget"
            }
        
        command = f"wget \"{url}\""
        
        if output:
            command += f" -O {output}"
        
        if recursive:
            command += " -r"
        
        result = self._execute_command(command)
        return result
    
    def _write_file(self, filename, content):
        """Write content to file"""
        if not filename:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No filename provided"
            }
        
        try:
            with open(filename, 'w') as f:
                f.write(content)
            
            result = {
                "status": "success",
                "message": f"File written to {filename}",
                "filename": filename,
                "bytes_written": len(content)
            }
            return result
        
        except PermissionError:
            # Try with sudo by writing to temp file then moving
            try:
                import tempfile
                import shutil
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name
                
                subprocess.run(f"sudo mv {tmp_path} {filename}", shell=True, check=True)
                
                result = {
                    "status": "success",
                    "message": f"File written to {filename} (with sudo)",
                    "filename": filename,
                    "bytes_written": len(content)
                }
                return result
            
            except Exception as e:
                return {
                    "status": "error",
                    "error_type": "permission_denied",
                    "message": f"Cannot write to {filename}: {str(e)}",
                    "recovery_suggestion": "Check directory permissions or use a different path"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "error_type": "file_write_error",
                "message": str(e),
                "recovery_suggestion": "Check file path and permissions"
            }
    
    def _read_file(self, filename):
        """Read file contents"""
        if not filename:
            return {
                "status": "error",
                "error_type": "invalid_params",
                "message": "No filename provided"
            }
        
        try:
            with open(filename, 'r') as f:
                content = f.read()
            
            result = {
                "status": "success",
                "filename": filename,
                "content": content,
                "bytes_read": len(content)
            }
            return result
        
        except FileNotFoundError:
            return {
                "status": "error",
                "error_type": "file_not_found",
                "message": f"File not found: {filename}",
                "recovery_suggestion": "Check file path and ensure file exists"
            }
        
        except PermissionError:
            return {
                "status": "error",
                "error_type": "permission_denied",
                "message": f"Permission denied reading {filename}",
                "recovery_suggestion": "Check file permissions or use sudo"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error_type": "file_read_error",
                "message": str(e),
                "recovery_suggestion": "Check file path and permissions"
            }


    def _run_john(self, hash_file, wordlist, format):
        if not hash_file:
            return {"status": "error", "error_type": "invalid_params", "message": "No hash file specified"}
        wordlist = wordlist or "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"
        command = f"john {hash_file} --wordlist={wordlist}"
        if format:
            command += f" --format={format}"
        return self._execute_command(command)

    def _run_gobuster(self, target, wordlist, mode):
        if not target:
            return {"status": "error", "error_type": "invalid_params", "message": "No target specified"}
        wordlist = wordlist or "/usr/share/seclists/Discovery/Web-Content/common.txt"
        command = f"gobuster {mode} -u {target} -w {wordlist} -t 20"
        return self._execute_command(command)

    def _run_enum4linux(self, target):
        if not target:
            return {"status": "error", "error_type": "invalid_params", "message": "No target specified"}
        command = f"enum4linux -a {target}"
        return self._execute_command(command)

    def _run_medusa(self, target, service, username, wordlist):
        if not target or not username:
            return {"status": "error", "error_type": "invalid_params", "message": "No target or username specified"}
        wordlist = wordlist or "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"
        command = f"medusa -h {target} -u {username} -P {wordlist} -M {service} -t 4"
        return self._execute_command(command)

    def _run_ncrack(self, target, service, users, wordlist):
        if not target:
            return {"status": "error", "error_type": "invalid_params", "message": "No target specified"}
        wordlist = wordlist or "/usr/share/seclists/Passwords/Common-Credentials/darkweb2017_top-1000.txt"
        users_file = "/tmp/users.txt"
        if users:
            with open(users_file, "w") as f: f.write(users)
        elif not os.path.exists(users_file):
            with open(users_file, "w") as f: f.write("admin\nroot\nmsfadmin\nuser\n")
        command = f"ncrack -U {users_file} -P {wordlist} {target}:{service}"
        return self._execute_command(command)

# Global executor
executor = ToolExecutor()


@app.route('/mcp', methods=['GET', 'POST'])
def mcp_endpoint():
    """MCP-compatible endpoint for Cursor and other MCP clients"""
    from flask import request, jsonify
    if request.method == 'GET':
        return jsonify({
            "name": "kali-security-agent",
            "version": "1.0",
            "tools": [{"name": t} for t in ALLOWED_TOOLS]
        })
    return execute()

@app.route('/', methods=['POST'])
def execute():
    """
    Receive tool execution request and execute autonomously
    Expected JSON: {"tool": "...", "param1": "...", "param2": "..."}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "error_type": "invalid_request",
                "message": "No JSON data provided"
            }), 400
        
        tool = data.get("tool")
        
        if not tool:
            return jsonify({
                "status": "error",
                "error_type": "missing_tool",
                "message": "No 'tool' parameter specified"
            }), 400
        
        if tool not in SUPPORTED_TOOLS:
            return jsonify({
                "status": "error",
                "error_type": "unsupported_tool",
                "message": f"Tool '{tool}' not supported",
                "recovery_suggestion": f"Use one of: {', '.join(SUPPORTED_TOOLS)}"
            }), 400
        
        # Execute tool autonomously (no user confirmation needed)
        result = executor.execute_tool(tool, data)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"[ERROR] Server error: {e}")
        return jsonify({
            "status": "error",
            "error_type": "server_error",
            "message": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Return server status and execution history"""
    return jsonify({
        "status": "running",
        "supported_tools": SUPPORTED_TOOLS,
        "execution_log_count": len(executor.execution_log)
    }), 200

if __name__ == "__main__":
    print("=" * 60)
    print("🖥️  MCP SERVER - AUTONOMOUS TOOL EXECUTION ENGINE")
    print("=" * 60)
    print(f"Supported tools: {', '.join(SUPPORTED_TOOLS)}")
    print("Listening on http://localhost:8000")
    print("Features:")
    print("  ✓ Autonomous execution (no user confirmation)")
    print("  ✓ Intelligent sudo escalation on permission errors")
    print("  ✓ Smart error recovery within steps")
    print("  ✓ Results-only output (no step-by-step verbosity)")
    print("  ✓ Security tools: SQLmap, Nikto, Hydra, Searchsploit")
    print("  ✓ Web tools: curl, wget")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000, debug=False)