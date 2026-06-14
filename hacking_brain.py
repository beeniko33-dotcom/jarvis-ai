import random
import time
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class HackingModule:
    name: str
    description: str
    commands: Dict[str, str]

class HackingBrain:
    def __init__(self):
        self.modules = self._init_modules()
        self.current_module = "scan"
        self.command_count = 0
        
    def _init_modules(self):
        return {
            "scan": HackingModule("SCAN", "Network scanning & enumeration", {
                "nmap": "nmap -sV [target] - Port scanning with service detection",
                "nmap -sS": "nmap -sS [target] - SYN stealth scan",
                "nmap -A": "nmap -A [target] - Aggressive scan with OS detection",
                "nikto": "nikto -h [target] - Web vulnerability scanner",
                "masscan": "masscan [target] - High-speed port scanner"
            }),
            "recon": HackingModule("RECON", "Reconnaissance & OSINT", {
                "whois": "whois [target] - Domain registration lookup",
                "theharvester": "theHarvester -d [target] - Email/subdomain harvesting",
                "dnsrecon": "dnsrecon -d [target] - DNS enumeration"
            }),
            "exploit": HackingModule("EXPLOIT", "Exploitation framework", {
                "msfconsole": "msfconsole - Metasploit framework",
                "exploit": "exploit [cve] - CVE exploitation module",
                "payload": "payload [type] - Generate reverse shell payloads"
            }),
            "crypto": HackingModule("CRYPTO", "Cryptographic tools", {
                "hashcat": "hashcat - Hash cracking tool",
                "openssl": "openssl - Encryption/decryption toolkit"
            })
        }
    
    def execute(self, cmd: str) -> Optional[str]:
        if cmd.lower() == "help":
            mod = self.modules[self.current_module]
            return f"[{mod.name}] {mod.description}\nCommands: " + ", ".join(mod.commands.keys())
        
        cmd_words = cmd.split()
        if not cmd_words:
            return None
            
        # Match command by first word
        for mod in self.modules.values():
            for pattern, description in mod.commands.items():
                pattern_words = pattern.split()
                if pattern_words and cmd_words[0] == pattern_words[0]:
                    self.command_count += 1
                    return f"[{mod.name.upper()}] {cmd}\nSimulated execution completed."
        return f"[ERROR] Unknown command: {cmd}"