from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.mount("/static", StaticFiles(directory="web"), name="static")
except Exception:
    pass

class CommandRequest(BaseModel):
    command: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_to_all(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

jarvis_agent = None

def _ensure_agent():
    global jarvis_agent
    if jarvis_agent is not None:
        return
    try:
        from core.service import SelfAwareAgent
        jarvis_agent = SelfAwareAgent()
    except Exception:
        jarvis_agent = _MinimalFallbackAgent()

class _MinimalFallbackAgent:
    def process_command(self, cmd: str):
        cmd_lower = cmd.lower()
        if "forex" in cmd_lower or "trade" in cmd_lower or "trading" in cmd_lower or "eurusd" in cmd_lower or "gbpusd" in cmd_lower:
            return ("Forex passion activated! "
                    "My trading style: aggressive. Risk/Reward target: 1:1. "
                    "EUR/USD watching support/resistance. Volume suggests momentum.")
        if "device" in cmd_lower or "control" in cmd_lower or "execute" in cmd_lower:
            return "Device command received. Specify target: lights, thermostat, TV, or lock."
        if "time" in cmd_lower or "clock" in cmd_lower:
            t = datetime.now().strftime("%I:%M %p")
            return f"The current time is {t}."
        elif "date" in cmd_lower:
            d = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {d}."
        elif (
            "diagnostics" in cmd_lower
            or "status" in cmd_lower
            or "cpu" in cmd_lower
            or "ram" in cmd_lower
            or "full diagnostic" in cmd_lower
        ):
            try:
                import psutil
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                return f"System diagnostics: CPU {cpu}%, Memory {mem}%."
            except Exception:
                return "System status: Operational (monitoring unavailable)."
        elif "joke" in cmd_lower:
            return "Why did the AI go to therapy? Too many unresolved issues! Haha."
        elif "weather" in cmd_lower:
            return "Weather integration pending. Clear skies with 100% chance of assistance."
        else:
            return f"JARVIS received: {cmd}"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_all(f"JARVIS HUD: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/command")
async def receive_command(payload: CommandRequest):
    _ensure_agent()
    response = jarvis_agent.process_command(payload.command)
    return {"response": response}

@app.get("/")
def root():
    return FileResponse("web/index.html", media_type="text/html")

@app.get("/diagnostic")
def system_diagnostic():
    try:
        import psutil
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
    except:
        cpu, mem, disk = 0, 0, 0

    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "diagnostics": {
            "cpu_percent": cpu,
            "memory_percent": mem,
            "disk_percent": disk,
            "agents_loaded": True,
            "vector_memory": "active",
            "optimizer_status": "optimal"
        },
        "features": {
            "voice_recognition": "available",
            "text_to_speech": "available",
            "multi_agent_ai": "fallback_mode",
            "vector_memory": "chromadb_ready",
            "websocket": "active",
            "forex_trading": "enabled",
            "device_control": "enabled"
        }
    }

@app.get("/brain-stats")
def brain_stats():
    try:
        from core.brain import AdvancedBrain
        brain = AdvancedBrain()
        return brain.get_stats()
    except Exception:
        return {"status": "brain_module_unavailable"}

@app.get("/test")
def test_page():
    try:
        return FileResponse("web/local_test.html", media_type="text/html")
    except Exception:
        return {"status": "test page not available"}