<img width="1200" height="783" alt="Final_EDIT" src="https://github.com/user-attachments/assets/fe9aafc5-294b-43f5-b20f-4ff1305bf0d8" />
-----

license: mit
language:

- en
  tags:
- security
- penetration-testing
- autonomous-agent
- mcp
- kali-linux
- llm
- cybersecurity
- red-team
  library_name: other
  pipeline_tag: text-generation

-----

# 🔐 PenMaster Security

**Autonomous AI-powered penetration testing agent — fully local, no cloud, no API keys.**

Built on Kali Linux with a local LLM (Qwen 2.5-14B via LM Studio) and a Flask-based MCP tool server. The agent runs recon, attacks, and generates professional pentest reports — all autonomously.

![demo](./Final_EDIT.gif)

-----

## What It Does

- 🔍 Autonomous recon — masscan + nmap to discover open ports and services
- ⚔️ Autonomous attack loop — selects and chains tools based on what it finds
- 🧠 Persistent negative experience cache — learns what fails across ALL sessions and never wastes time on it again
- 📝 Auto-generates branded HTML pentest reports on session end (Ctrl+C)
- 🔒 100% local — Qwen 2.5-14B running in LM Studio, nothing leaves your machine

-----

## Tool Arsenal (18 tools)

|Tool              |Purpose                        |
|------------------|-------------------------------|
|`run_masscan`     |Fast port discovery            |
|`run_nmap`        |Deep service/version scanning  |
|`run_nikto`       |Web vulnerability scanning     |
|`run_sqlmap`      |SQL injection testing          |
|`run_hydra`       |Credential brute forcing       |
|`run_ncrack`      |Network authentication cracking|
|`run_medusa`      |Fast parallel brute forcing    |
|`run_searchsploit`|Exploit lookup                 |
|`run_gobuster`    |Web directory brute forcing    |
|`run_enum4linux`  |SMB/Samba enumeration          |
|`run_john`        |Hash cracking                  |
|`run_command`     |Execute any shell command      |
|`write_file`      |Write output to files          |
|`read_file`       |Read file contents             |
|`run_metasploit`  |Framework exploitation         |
|`run_wpscan`      |WordPress scanning             |
|`run_whatweb`     |Web technology fingerprinting  |
|`run_setoolkit`   |Social engineering attacks     |

-----

## Architecture

```
agent_loop.py  ──►  mcp_server.py (Flask, port 8000)  ──►  security tools
     │
     ├──►  agent_cache.py       (persistent negative experience cache)
     └──►  report_generator.py  (auto HTML pentest report on exit)
```

-----

## Sovereign Agent Layer v1

The negative experience cache fingerprints every tool call. If it fails once, it gets one retry. Fail twice — permanently blacklisted across all future sessions. The agent never wastes cycles on dead ends it has already proven don’t work.

-----

## Stack

- **Model**: Qwen 2.5-14B Instruct Abliterated (GGUF via LM Studio)
- **Agent**: Python autonomous loop with MCP tool calls
- **MCP Server**: Flask on port 8000
- **OS**: Kali Linux (UTM on Apple Silicon M1)
- **Hardware**: MacBook Pro M1 16GB RAM

-----

## Usage

```bash
cd /home/bigkali/security-agent
python3 agent_loop.py

>>> engage 192.168.64.3    # full autonomous recon + attack
>>> run nmap on 10.0.0.1   # single goal query
>>> exit                   # triggers HTML report generation
```

-----

## Project Status

Active development. New capabilities and upgrades pushed regularly.

Built by a self-taught developer and security researcher. One year in.

-----

## License

MIT

