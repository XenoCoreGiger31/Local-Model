# Autonomous Security Agent - Setup Guide

## Prerequisites

- Kali Linux
- LM Studio installed
- Qwen 2.5-7B model loaded in LM Studio
- Python 3.8+
- Suricata IDS
- IPTables firewall

## Step 1: Firewall Configuration

sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

## Step 2: Suricata IDS

sudo systemctl start suricata
sudo systemctl enable suricata

## Step 3: LM Studio

Load Qwen 2.5-7B on 192.168.0.39:1234

## Step 4: Run Agent

python agent_loop.py
