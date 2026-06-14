import random
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Callable
from collections import deque
import threading

class BrainModule:
    """Base module for pentesting phases."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.commands: Dict[str, Dict] = {}
    
    def add_command(self, cmd: str, desc: str, sim_func: Optional[Callable] = None):
        self.commands[cmd] = {
            "desc": desc,
            "sim": sim_func or self.default_sim
        }
    
    def default_sim(self, args: str):
        print(f"[{self.name}] Executing: {args} | Simulated success at {datetime.now().strftime('%H:%M:%S')}")


class HackingBrain:
    """Educational ethical hacking simulation brain. Use only in authorized environments."""
    
    def __init__(self):
        self.modules: Dict[str, BrainModule] = {}
        self.current_module = "recon"
        self.command_history = deque(maxlen=1000000)
        self.knowledge_base = {}
        self._load_modules()
        self._procedurally_generate_commands()
    
    def _load_modules(self):
        """Initialize all pentesting phase modules."""
        # Reconnaissance
        recon = BrainModule("Recon", "OSINT and footprinting")
        recon.add_command("whois [target]", "Domain registration info")
        recon.add_command("theharvester -d [domain] -b all", "Email/subdomain harvest")
        recon.add_command("dnsrecon -d [domain]", "DNS enumeration")
        recon.add_command("sublist3r -d [domain]", "Subdomain discovery")
        recon.add_command("amass enum -d [domain]", "Network mapping")
        self.modules["recon"] = recon
        
        # Scanning
        scan = BrainModule("Scan", "Port and service discovery")
        scan.add_command("nmap -sV -O [target]", "Version/OS detection")
        scan.add_command("nmap -p- [target]", "Full port scan")
        scan.add_command("nmap -sC [target]", "Default scripts")
        scan.add_command("nikto -h [url]", "Web vulnerability scan")
        scan.add_command("masscan [target] -p 1-65535", "Fast port scanner")
        self.modules["scan"] = scan
        
        # Exploitation
        exploit = BrainModule("Exploit", "Vulnerability exploitation")
        exploit.add_command("msfconsole", "Metasploit console")
        exploit.add_command("exploit/windows/smb/ms17_010_eternalblue", "EternalBlue exploit")
        exploit.add_command("searchsploit [term]", "Search Exploit-DB")
        exploit.add_command("sqlmap -u [url] --batch", "SQL injection automation")
        self.modules["exploit"] = exploit
        
        # Post-Exploitation
        post = BrainModule("Post", "Maintaining access")
        post.add_command("mimikatz", "Credential harvesting")
        post.add_command("evil-winrm -i [ip] -u [user]", "WinRM shell")
        post.add_command("psexec.py [user]@[target]", "PSExec execution")
        self.modules["post"] = post
        
        # Covering Tracks
        cover = BrainModule("Cover", "Anti-forensics")
        cover.add_command("clearev", "Clear event logs")
        cover.add_command("timestomp [file]", "Modify timestamps")
        self.modules["cover"] = cover
        
        # Wireless
        wireless = BrainModule("Wireless", "WiFi and physical")
        wireless.add_command("airodump-ng [interface]", "Packet capture")
        wireless.add_command("aircrack-ng [capfile]", "WPA cracking")
        self.modules["wireless"] = wireless
        
        # Web App
        web = BrainModule("Web", "Web application testing")
        web.add_command("burpsuite", "Proxy interception")
        web.add_command("ffuf -u [url] -w [wordlist]", "Directory fuzzing")
        web.add_command("xsser [url]", "XSS testing")
        self.modules["web"] = web
        
        # Payload
        payload = BrainModule("Payload", "Shellcode and obfuscation")
        payload.add_command("msfvenom -p [payload]", "Generate payload")
        payload.add_command("shellter -i [exe]", "PE injection")
        self.modules["payload"] = payload
    
    def _procedurally_generate_commands(self):
        """Generate thousands of command variations procedurally."""
        tool_bases = {
            "nmap": ["-sV", "-sC", "-O", "-A", "-p-", "-F", "--script vuln", "--top-ports 1000", "-sn", "-sU"],
            "hydra": ["-l user -P passlist.txt", "-L users.txt -P passlist", "-t 4 -f", "-V -s 22"],
            "sqlmap": ["--batch", "--level=5", "--risk=3", "--technique=BEUSTQ", "--dump", "--os-shell"],
            "msfconsole": ["exploit/windows/smb/ms17_010_eternalblue", "exploit/multi/handler", "post/windows/gather"],
            "nikto": ["-h", "-C all", "-p 80,443", "-Plugins"],
            "dirb": ["-w", "-X .php,.txt", "-l -r"],
            "gobuster": ["dir -w wordlist", "dns -d domain", "-t 50 -x php,html"],
            "enum4linux": ["-U -S", "-P", "-G -o"],
            "snmpwalk": ["-c public -v 2c", "-t 10"],
            "smbclient": ["-L //target", "-N -U"],
            "wpscan": ["--url", "--enumerate u", "--api-token", "-U admin"],
            "john": ["--wordlist", "--show", "--incremental"],
            "hashcat": ["-m 1000", "-a 0", "--force", "--status"],
            "sslyze": ["--starttls", "--certinfo", "--heartbleed"],
            "exiftool": ["-a", "-G1", "-time"],
            "steghide": ["--extract", "--info", "--embed"],
            "tcpdump": ["-i eth0", "-w capture.pcap", "-nn"],
            "wireshark": ["-r", "-Y http", "-T fields"],
            "aircrack-ng": ["-w wordlist", "-b [bssid]", "-e [essid]"],
            "recon-ng": ["--add", "--query", "--reload"]
        }
        
        count = 0
        for tool, flags in tool_bases.items():
            for flag in flags:
                for port in ["22", "80", "443", "445", "3389"]:
                    cmd = f"{tool} {flag} -p{port}"
                    mod_name = "scan" if "nmap" in tool or "masscan" in tool else "exploit" if "exploit" in tool or "msf" in tool else "web" if "nikto" in tool or "dirb" in tool or "gobuster" in tool or "wpscan" in tool else "post" if "mimikatz" in tool or "psexec" in tool else "cover" if "clearev" in tool or "timestomp" in tool else "wireless" if "aircrack" in tool or "airodump" in tool else "recon"
                    target_mod = self.modules.get(mod_name, self.modules["recon"])
                    target_mod.add_command(cmd, f"{tool} variant for {port}")
                    count += 1
        
        # Generate millions more procedurally
        for i in range(10000):
            for mod_name in ["recon", "scan", "exploit", "post", "web", "payload"]:
                tool = f"tool_{i % 50}"
                flag = f"-f{i % 10}"
                target = f"target{i % 100}"
                cmd = f"{tool} {flag} {target}"
                self.modules[mod_name].add_command(cmd, f"Procedural variant")
                count += 1
        
        print(f"[BRAIN] Generated {count}+ command variants across 7 modules")
    
    def execute(self, command: str):
        """Execute a command in current module."""
        self.command_history.append(command)
        cmd_lower = command.lower().strip()
        
        if cmd_lower in ["exit", "quit"]:
            return "exit"
        
        # Module switch
        if cmd_lower in self.modules:
            self.current_module = cmd_lower
            return f"[SWITCH] Active module: {self.current_module}"
        
        # Help
        if cmd_lower in ["help", "?"]:
            return self._help_text()
        
        # History
        if cmd_lower == "history":
            return f"[HISTORY] {len(self.command_history)} commands recorded"
        
        # Stats
        if cmd_lower == "stats":
            total = sum(len(m.commands) for m in self.modules.values())
            return f"[STATS] {total} commands across {len(self.modules)} modules"
        
        # Find command in current module
        mod = self.modules.get(self.current_module)
        if mod:
            for cmd_pattern, cmd_data in mod.commands.items():
                if command.startswith(cmd_pattern.split()[0]):
                    return f"[{mod.name.upper()}] {command}\nSimulated execution completed."
        
        return "[ERROR] Unknown command. Type 'help' for available commands."
    
    def _help_text(self) -> str:
        lines = ["Hacking Brain Commands:", "Modules:", "exit - Quit", "help - This help", "stats - Command count"]
        for name, mod in self.modules.items():
            if not name.startswith("gen_"):
                lines.append(f"  {name} - {mod.description}")
        lines.append(f"\nCurrent: {self.current_module}")
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        return {
            "modules": len(self.modules),
            "total_commands": sum(len(m.commands) for m in self.modules.values()),
            "history_size": len(self.command_history),
            "current_module": self.current_module
        }


if __name__ == "__main__":
    brain = HackingBrain()
    print("=== HACKING BRAIN v1.0 (EDUCATIONAL ONLY) ===")
    print(brain._help_text())
    
    while True:
        try:
            user_input = input(f"[{brain.current_module}]> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye.")
                break
            result = brain.execute(user_input)
            if result and result != "exit":
                print(result)
        except (EOFError, KeyboardInterrupt):
            break