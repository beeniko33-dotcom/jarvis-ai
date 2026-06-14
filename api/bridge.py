from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# Allow local frontend to call the bridge during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the `web` static test page at /test
try:
    app.mount('/static', StaticFiles(directory='web'), name='static')
except Exception:
    # If static mount fails in some environments, ignore; route below will still work
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

# Instantiate the agent lazily when the module is first used. Avoid importing
# `core.service` at module import time so missing optional packages don't
# prevent the FastAPI app from loading.
jarvis_agent = None
def _ensure_agent():
    global jarvis_agent
    if jarvis_agent is not None:
        return
    # Avoid importing `core.service` (which pulls heavy optional deps) unless
    # `crewai` is actually available. Check `core.agent.CREWAI_AVAILABLE` first.
    try:
        from core.agent import CREWAI_AVAILABLE
        if CREWAI_AVAILABLE:
            from core.service import SelfAwareAgent
            jarvis_agent = SelfAwareAgent()
            return
    except Exception:
        # If anything goes wrong, fall through to fallback
        pass

    import logging
    logging.getLogger(__name__).warning('SelfAwareAgent unavailable or crewai missing; using fallback agent')
    # Provide a lightweight fallback agent that uses the SimpleCrew
    try:
        from core.agent import JarvisAgents

        class _FallbackAgent:
            def process_command(self, cmd: str):
                crew = JarvisAgents().create_crew(cmd)
                try:
                    return str(crew.kickoff())
                except Exception:
                    return f"Fallback result for: {cmd}"

        jarvis_agent = _FallbackAgent()
    except Exception:
        jarvis_agent = None

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_to_all(f'JARVIS HUD: {data}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post('/command')
async def receive_command(payload: CommandRequest):
    _ensure_agent()
    if jarvis_agent is None:
        try:
            from core.agent import JarvisAgents
            crew = JarvisAgents().create_crew(payload.command)
            # SimpleCrew provides a kickoff() method that returns a string
            response = crew.kickoff()
            return {'response': response}
        except Exception:
            return {'response': 'JARVIS service unavailable (missing optional dependency).'}
    response = jarvis_agent.process_command(payload.command)
    return {'response': response}

@app.get('/')
def root():
    return {'status': 'JARVIS backend bridge active'}


@app.get('/test')
def test_page():
    # Return the local test HTML if present
    try:
        return FileResponse('web/local_test.html', media_type='text/html')
    except Exception:
        return {'status': 'test page not available'}
