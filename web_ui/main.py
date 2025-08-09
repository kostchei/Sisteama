import sys
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Add root project directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.dice_engine import DiceEngine, DiceResult

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="web_ui/static"), name="static")

# Templates
templates = Jinja2Templates(directory="web_ui/templates")

# Dice Engine
dice_engine = DiceEngine()

@app.get("/")
async def get(request: Request):
    """Serve the main chat page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle websocket connections"""
    await websocket.accept()
    await websocket.send_json({"sender": "System", "message": "Welcome to Tale Keeper Chat!"})

    while True:
        try:
            data = await websocket.receive_text()

            # User message
            await websocket.send_json({"sender": "You", "message": data})

            response = handle_command(data)

            # System response
            await websocket.send_json({"sender": "System", "message": response})

        except Exception as e:
            print(f"Websocket error: {e}")
            break

def handle_command(command: str) -> str:
    """Parse and handle user commands"""
    command = command.strip()
    if not command.startswith("/"):
        return "Unknown command. Try '/roll 1d20' or '/roll 2d6+3'."

    parts = command.split(" ")
    cmd = parts[0]

    if cmd == "/roll":
        if len(parts) < 2:
            return "Usage: /roll <dice_notation>"

        dice_string = parts[1]
        try:
            result = dice_engine.roll_damage(dice_string)
            return f"Rolling {dice_string}... Result: {result.total} ({result.description})"
        except ValueError as e:
            return f"Error: {e}"

    return f"Unknown command: {cmd}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
