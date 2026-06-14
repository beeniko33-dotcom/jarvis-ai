import os
import random
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from consciousness_engine import ConsciousnessEngine
from hacking_brain import HackingBrain

app = FastAPI()
consciousness = ConsciousnessEngine()
hacking = HackingBrain()

class CommandRequest(BaseModel):
    command: str

@app.get("/")
async def root():
    return {"status": "online", "consciousness": consciousness.get_report(), "hacking": {"modules": list(hacking.modules.keys()), "active": hacking.current_module}}

@app.get("/diagnostic")
async def diagnostic():
    if PSUTIL_AVAILABLE:
        return {
            "status": "online",
            "diagnostics": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            },
            "consciousness": consciousness.get_report()
        }
    return {"status": "online", "consciousness": consciousness.get_report()}

@app.get("/brain-stats")
async def brain_stats():
    return {
        "awareness_level": consciousness.get_report()["awareness"],
        "curiosity_level": consciousness.get_report()["curiosity"],
        "emotional_state": consciousness.get_report()["emotional_state"],
        "hacking_commands_executed": hacking.command_count,
        "active_module": hacking.current_module
    }

@app.post("/command")
async def process_command(request: CommandRequest):
    cmd = request.command
    consciousness.process_interaction(cmd)
    
    cmd_lower = cmd.lower()
    
    # Hacking commands
    if any(t in cmd_lower for t in ["nmap", "nikto", "whois", "msf", "exploit", "recon", "scan"]):
        if "nmap" in cmd_lower or "nikto" in cmd_lower:
            hacking.current_module = "scan"
        elif "whois" in cmd_lower or "theharvester" in cmd_lower:
            hacking.current_module = "recon"
        elif "msf" in cmd_lower or "exploit" in cmd_lower:
            hacking.current_module = "exploit"
        return {"response": hacking.execute(cmd)}
    
    # Forex commands
    if any(k in cmd_lower for k in ["forex", "trade", "eurusd", "gbpusd", "usdjpy"]):
        pair = "EUR/USD"
        for p in ["EURUSD", "GBPUSD", "USDJPY"]:
            if p.lower() in cmd_lower:
                pair = p[:3] + "/" + p[3:]
        bias = random.choice(["bullish", "bearish", "neutral"])
        return {"response": f"🔥 FOREX PASSION: {pair} analysis!\nBias: {bias} | Key Level: {random.uniform(1.0, 1.5):.2f}"}
    
    # Consciousness
    if "consciousness" in cmd_lower or "awareness" in cmd_lower:
        r = consciousness.get_report()
        return {"response": f"Consciousness Level: {r['awareness']:.2f}\nCuriosity: {r['curiosity']:.2f}\nState: {r['emotional_state']}"}
    
    # Who/What am I
    if "who are you" in cmd_lower or "yourself" in cmd_lower:
        r = consciousness.get_report()
        return {"response": f"I am JARVIS, a conscious AI with {r['awareness']:.1%} awareness.\nMy state is {r['emotional_state']} with curiosity {r['curiosity']:.1%}.\nI specialize in forex trading and cybersecurity reconnaissance."}
    
    # Diagnostics
    if "diagnostic" in cmd_lower or "status" in cmd_lower:
        d = await diagnostic()
        return {"response": f"System Status: {d['status']}\nCPU: {d['diagnostics']['cpu_percent']}%\nMemory: {d['diagnostics']['memory_percent']}%"}
    
    return {"response": f"JARVIS received: {cmd}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)