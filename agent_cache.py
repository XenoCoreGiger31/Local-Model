import json
import hashlib
import os
import logging
from datetime import datetime

# ============================================================
# 🧠 PERSISTENT NEGATIVE EXPERIENCE CACHE
# PenMaster Security — Sovereign Agent Layer v1
#
# Analogy: a veteran soldier's scar tissue.
# The agent remembers every failed approach across ALL sessions.
# Try once → fail → retry once more.
# Fail twice → permanently blacklisted. Never wasted on again.
# ============================================================

CACHE_DIR = "/home/bigkali/security-agent"
CACHE_FILE = os.path.join(CACHE_DIR, "failure_cache.json")

log = logging.getLogger("agent")


class NegativeCache:
    """
    Persistent cross-session failure memory.

    Structure of cache.json:
    {
      "<fingerprint>": {
        "tool": "run_hydra",
        "summary": "hydra | target=192.168.64.3 service=ftp",
        "attempts": 2,
        "permanently_blocked": true,
        "first_seen": "2025-06-08 14:32:01",
        "last_seen":  "2025-06-08 14:45:12",
        "reason": "stdout empty, status failed"
      },
      ...
    }
    """

    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self._cache = self._load()
        log.info(f"[MEMORY] 🧠 Negative cache loaded — {len(self._cache)} blocked fingerprints")

    # ----------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------

    def _load(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                log.warning("[MEMORY] 😤 Cache file corrupt — starting fresh")
                return {}
        return {}

    def _save(self):
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            log.error(f"[ERROR] 😭🔥 Cache save failed: {e}")

    def _fingerprint(self, step: dict) -> str:
        """
        Stable hash of the tool call so identical attempts
        match across sessions regardless of field ordering.

        We exclude fields that carry no semantic meaning
        (e.g. internal timestamps injected by wrappers).
        """
        relevant = {k: v for k, v in step.items() if k != "_meta"}
        canonical = json.dumps(relevant, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def _summary(self, step: dict) -> str:
        tool = step.get("tool", "unknown")
        params = " | ".join(f"{k}={v}" for k, v in step.items() if k != "tool")
        return f"{tool} | {params}"

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def should_attempt(self, step: dict) -> bool:
        """
        Returns True  → go ahead, attempt this tool call.
        Returns False → permanently blocked, skip it entirely.

        Call this BEFORE execute_step().
        """
        fp = self._fingerprint(step)
        entry = self._cache.get(fp)
        if entry and entry.get("permanently_blocked"):
            log.warning(
                f"[MEMORY] 🚫 BLOCKED (seen {entry['attempts']}x) → {entry['summary']}"
            )
            return False
        return True

    def record_failure(self, step: dict, reason: str = ""):
        """
        Record one failed attempt.
        After 2 failures the fingerprint is permanently blocked.

        Call this after a failed execute_step().
        """
        fp = self._fingerprint(step)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if fp not in self._cache:
            self._cache[fp] = {
                "tool": step.get("tool", "unknown"),
                "summary": self._summary(step),
                "attempts": 0,
                "permanently_blocked": False,
                "first_seen": now,
                "last_seen": now,
                "reason": reason,
            }

        entry = self._cache[fp]
        entry["attempts"] += 1
        entry["last_seen"] = now
        if reason:
            entry["reason"] = reason

        if entry["attempts"] >= 2:
            entry["permanently_blocked"] = True
            log.warning(
                f"[MEMORY] ☠️  PERMANENTLY BLOCKED after {entry['attempts']} failures → {entry['summary']}"
            )
        else:
            log.info(
                f"[MEMORY] 📝 Failure #{entry['attempts']} recorded (1 retry left) → {entry['summary']}"
            )

        self._save()

    def record_success(self, step: dict):
        """
        If a previously-failed fingerprint suddenly works
        (e.g. different target context), clear its block.
        Uncommon but fair.
        """
        fp = self._fingerprint(step)
        if fp in self._cache:
            log.info(f"[MEMORY] ✅ Clearing prior failure record — tool succeeded: {self._summary(step)}")
            del self._cache[fp]
            self._save()

    def stats(self) -> dict:
        total = len(self._cache)
        blocked = sum(1 for e in self._cache.values() if e.get("permanently_blocked"))
        pending = total - blocked
        return {
            "total_fingerprints": total,
            "permanently_blocked": blocked,
            "one_strike_pending": pending,
        }

    def dump(self):
        """Pretty-print the full cache to the log — useful for debugging."""
        log.info(f"[MEMORY] 🧠 Cache dump ({len(self._cache)} entries):")
        for fp, entry in self._cache.items():
            status = "☠️  BLOCKED" if entry["permanently_blocked"] else f"⚠️  {entry['attempts']} attempt(s)"
            log.info(f"  [{fp}] {status} → {entry['summary']}")
