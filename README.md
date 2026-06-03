![banner](./banner_animated.gif)

![banner](./banner_final.png)

![demo](./Final_EDIT.gif)


(1) Issue and Rationale

One issue that could use further study is whether listening to music while studying helps students perform better on tests. Many students listen to music when doing homework or preparing for exams, but it is not always clear if music helps concentration or becomes a distraction. I would design an experiment to learn whether music has a positive, negative, or no effect on test performance.

(2) Hypothesis

My hypothesis is that students who listen to calm instrumental music while studying will score higher on a test than students who study in complete silence.

(3) Independent and Dependent Variables

The independent variable is the study environment. One group of students will study while listening to calm instrumental music, and another group will study in silence.

The dependent variable is the students' test scores. After studying, all participants will take the same test, and their scores will be compared.

(4) Ethical Issues

Several ethical issues would need to be considered. First, all participants would need to give informed consent before participating in the experiment. They should understand what the study involves and know that they can leave the study at any time. Participants' test scores and personal information should remain confidential. Researchers should also make sure that no participant is harmed or treated unfairly during the study.

(5) Expected Conclusion

I believe the students who study while listening to calm instrumental music will perform slightly better on the test. The music may help them relax and focus on the material. However, it is also possible that some students may learn better in silence because everyone studies differently. The results would help determine whether listening to music is an effective study method for most students.

![demo](./Final_EDIT.gif)

# Autonomous Security Agent
A fully local autonomous cybersecurity agent that executes real security tooling (nmap, masscan) through an MCP-controlled Qwen 2.5-7B reasoning loop. Designed for offline execution, iterative decision-making, and tool-driven analysis without external APIs.
Enables autonomous security workflows where an LLM can plan, execute, and analyze real penetration testing tools locally.
A fully local autonomous cybersecurity agent built around Qwen 2.5-7B and an MCP execution layer.

It enables an LLM to plan, execute, and analyze real security tools (nmap, masscan) in a closed-loop reasoning system without external APIs.

Designed for experimentation in offline agentic security systems, tool orchestration, and constrained LLM autonomy.

## Features

- **Local LLM Backend** — Qwen 2.5-7B served via LM Studio at `192.168.0.39:1234`
- **Autonomous Tool Execution** — Runs security tools (nmap, masscan) through MCP
- **Agent Loop** — Agent Loop — Autonomous reasoning cycle for planning, execution, and analysis
- **MCP Server** — Tool chain execution with `run_masscan`, `run_nmap`, `write_file`, `read_file`

## Components

- `agent_loop.py` — Main agent reasoning loop
- `mcp_server.py` — Tool execution server
- `tools_manifest.json` — Tool definitions
- `request.json` — Sample request format

## System Flow

User Request
    ↓
Agent Loop (Qwen 2.5-7B via LM Studio)
    ↓
MCP Server (Tool Orchestration Layer)
    ↓
Security Tools Execution (nmap, masscan)
    ↓
Result Analysis (Local LLM Reasoning)
    ↓
Iterative Decision Loop

## Security Setup

### Firewall Configuration

- **Outbound**: All traffic allowed
- **Inbound**: All traffic blocked (default deny)
- **IDS**: Suricata for behavioral alerting


### Network Security

- TOR integration for privacy
- Local-only LLM inference (no external API calls)
- MCP server bound to localhost only

## Current Status

Active experimental framework under continuous local development.

Current focus areas:
- autonomous tool orchestration
- MCP-based execution workflows
- local/offline agent reasoning
- constrained security automation research

## Minimal Requirements

This project is intentionally lightweight and designed for local experimentation.

Tested with:
- Kali Linux VM
- LM Studio
- Qwen 2.5-7B
- Python-based MCP server
- Consumer-grade hardware

No cloud APIs or paid infrastructure required.

THE FRAMEWORK IS DESIGNED TO REMAIN UNDERSTANDABLE, HACKABLE, AND PORTABLE FOR INDEPENDENT RESEARCHERS AND LOCAL AI EXPERIMENTATION.

## Installation & Setup

1. Install Kali Linux with Suricata
2. Install LM Studio and load Qwen 2.5-7B
3. Configure firewall rules (see docs/firewall-setup.md)
4. Clone this repository
5. Install Python dependencies
6. Run the agent: `python agent_loop.py`

## Documentation

See the `docs/` folder for:
- Detailed setup instructions
- Firewall rule examples
- Suricata configuration
- MCP server setup

## Framework Mode

This project is designed to be extended as a modular autonomous security framework.

Users can replace or extend:
- LLM backend (Qwen → Llama, Mistral, etc.)
- MCP tools (nmap, masscan → custom tooling)
- Agent loop logic (single-step → multi-agent systems)
- Execution environment (local VM → isolated containerized setups)

The system is intentionally minimal to support experimentation and customization.

## Extension Ideas

- Add additional MCP tools (recon, OSINT, log parsing)
- Introduce multi-agent roles (planner, executor, analyzer)
- Containerize execution layer for isolation
- Replace CLI tools with API-driven security services

## License

MIT License

MIT
