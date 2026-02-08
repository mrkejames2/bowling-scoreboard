import os

FILES = {
    "app/main.py": """from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from state import STATE
from scoring import score_game

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/scoreboard", response_class=HTMLResponse)
async def scoreboard(request: Request):
    total = score_game(STATE.frames)
    return templates.TemplateResponse("scoreboard.html", {
        "request": request,
        "frames": STATE.frames,
        "total": total
    })


@app.get("/admin/bowler", response_class=HTMLResponse)
async def admin_bowler(request: Request):
    return templates.TemplateResponse("admin_bowler.html", {"request": request})


@app.post("/api/shot")
async def record_shot(payload: dict):
    frame = STATE.current_frame
    shot = payload["shot"]

    if isinstance(shot, list):
        shot = len(shot)

    STATE.frames[frame]["shots"].append(shot)

    if frame < 9:
        if shot == "X":
            STATE.current_frame += 1
        else:
            if len(STATE.frames[frame]["shots"]) == 2:
                STATE.current_frame += 1
    else:
        pass

    return JSONResponse({"ok": True})


@app.post("/api/reset")
async def reset():
    STATE.reset()
    return {"ok": True}
""",

    "app/state.py": """from typing import List

class BowlingState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.frames: List[dict] = [
            {"shots": [], "score": None} for _ in range(10)
        ]
        self.current_frame = 0

STATE = BowlingState()
""",

    "app/scoring.py": """def score_game(frames):
    total = 0
    for i in range(10):
        shots = frames[i]["shots"]

        if i == 9:
            frames[i]["score"] = sum(shots)
            total += frames[i]["score"]
            continue

        if shots == ["X"]:
            bonus = next_two_shots(frames, i)
            frames[i]["score"] = 10 + bonus
            total += frames[i]["score"]
            continue

        if len(shots) == 2 and shots[1] == "/":
            bonus = next_one_shot(frames, i)
            frames[i]["score"] = 10 + bonus
            total += frames[i]["score"]
            continue

        frames[i]["score"] = sum(shots)
        total += frames[i]["score"]

    return total


def next_two_shots(frames, index):
    shots = []
    for f in frames[index+1:]:
        for s in f["shots"]:
            if s == "X":
                shots.append(10)
            elif s == "/":
                shots.append(10 - shots[-1])
            else:
                shots.append(s)
            if len(shots) == 2:
                return sum(shots)
    return sum(shots)


def next_one_shot(frames, index):
    for f in frames[index+1:]:
        s = f["shots"][0]
        if s == "X":
            return 10
        return s
    return 0
""",

    "app/templates/scoreboard.html": """<!DOCTYPE html>
<html>
<head>
  <title>Bowling Scoreboard</title>
  <style>
    body { font-family: sans-serif; background: #111; color: white; }
    .frame { display: inline-block; width: 60px; margin: 5px; text-align: center; }
  </style>
</head>
<body>
  <h1>Scoreboard</h1>
  <div>
    {% for f in frames %}
      <div class="frame">
        <div>{{ f.shots }}</div>
        <div>{{ f.score }}</div>
      </div>
    {% endfor %}
  </div>
  <h2>Total: {{ total }}</h2>
</body>
</html>
""",

    "app/templates/admin_bowler.html": """<!DOCTYPE html>
<html>
<head>
  <title>Bowler Admin</title>
  <script src="/static/admin_bowler.js"></script>
  <style>
    body { font-family: sans-serif; }
    .pin { width: 40px; height: 40px; border: 1px solid #333; display: inline-flex;
           align-items: center; justify-content: center; margin: 4px; cursor: pointer; }
    .active { background: red; color: white; }
  </style>
</head>
<body>
  <h1>Bowler Admin</h1>

  <div id="pins"></div>

  <button onclick="sendStrike()">X Strike</button>
  <button onclick="sendSpare()">/ Spare</button>
  <button onclick="submitPins()">Submit Pins</button>
  <button onclick="resetGame()">Reset</button>
</body>
</html>
""",

    "app/static/admin_bowler.js": """let selectedPins = new Set();

function renderPins() {
  const layout = [1,2,3,4,5,6,7,8,9,10];
  const container = document.getElementById("pins");
  container.innerHTML = "";

  layout.forEach(pin => {
    const div = document.createElement("div");
    div.className = "pin";
    div.innerText = pin;

    div.onclick = () => {
      if (selectedPins.has(pin)) selectedPins.delete(pin);
      else selectedPins.add(pin);
      div.classList.toggle("active");
    };

    container.appendChild(div);
  });
}

async function submitPins() {
  const pins = Array.from(selectedPins);
  await fetch("/api/shot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({shot: pins})
  });
  selectedPins.clear();
  renderPins();
}

async function sendStrike() {
  await fetch("/api/shot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({shot: "X"})
  });
}

async function sendSpare() {
  await fetch("/api/shot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({shot: "/"})
  });
}

async function resetGame() {
  await fetch("/api/reset", { method: "POST" });
}

window.onload = renderPins;
""",

    "docker-compose.yml": """services:
  bowling:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""
}

def ensure_dirs():
    for path in FILES.keys():
        folder = os.path.dirname(path)
        if folder:  # avoid trying to create ""
            os.makedirs(folder, exist_ok=True)

def write_files():
    for path, content in FILES.items():
        with open(path, "w") as f:
            f.write(content)
        print(f"Created: {path}")

if __name__ == "__main__":
    ensure_dirs()
    write_files()
    print("\nBowling MVP project structure created successfully!")
