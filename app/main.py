from fastapi import FastAPI, Request
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
    return templates.TemplateResponse("scoreboard.html", {"request": request})


@app.get("/admin/bowler", response_class=HTMLResponse)
async def admin_bowler(request: Request):
    return templates.TemplateResponse("admin_bowler.html", {"request": request})


@app.post("/api/set_mode")
async def set_mode(payload: dict):
    mode = payload.get("mode", "baker")
    if mode not in ["baker", "peterson"]:
        mode = "baker"

    STATE.reset()
    STATE.mode = mode
    return {"ok": True, "mode": STATE.mode}


@app.post("/api/set_active_bowler")
async def set_active_bowler(payload: dict):
    bowler = payload.get("bowler", "A")
    if bowler in STATE.bowlers:
        STATE.active_bowler = bowler
    return {"ok": True, "active_bowler": STATE.active_bowler}


# ---------------------------------------------------------
# Shot Conversion Logic (with 10th-frame spare fix)
# ---------------------------------------------------------
def convert_shot_symbol(shots, knocked_count, frame_index):
    # STRIKE
    if knocked_count == 10:
        return "X"

    # 10th frame spare on 3rd ball
    if frame_index == 9 and len(shots) == 2:
        second_ball = shots[1]
        if isinstance(second_ball, int) and second_ball + knocked_count == 10:
            return "/"

    # Normal spare
    if len(shots) == 1 and shots[0] != "X" and isinstance(shots[0], int):
        if shots[0] + knocked_count == 10:
            return "/"

    return knocked_count


# ---------------------------------------------------------
# Frame Advancement Logic
# ---------------------------------------------------------
def advance_frame_for_frames(frames, current_frame, shot_symbol):
    frame = current_frame
    shots = frames[frame]["shots"]

    # Frames 1–9
    if frame < 9:
        if shot_symbol == "X" or len(shots) == 2:
            return frame + 1, True
        return frame, False

    # 10th frame
    if frame == 9:
        if len(shots) == 3:
            return frame, True
        if len(shots) == 2 and shots[0] != "X" and shots[1] != "/":
            return frame, True
        return frame, False

    return frame, False


# ---------------------------------------------------------
# Record Shot (with snapshot save)
# ---------------------------------------------------------
@app.post("/api/shot")
async def record_shot(payload: dict):
    # Save snapshot BEFORE modifying state
    STATE.save_snapshot()

    standing = payload.get("standing_pins", [])
    knocked = payload.get("knocked_pins", [])
    knocked_count = len(knocked)

    STATE.standing_pins = set(standing)

    if STATE.mode == "baker":
        frames = STATE.frames
        frame_index = STATE.current_frame
    else:
        bowler_id = payload.get("bowler") or STATE.active_bowler
        bowler_state = STATE.bowlers[bowler_id]
        frames = bowler_state["frames"]
        frame_index = bowler_state["current_frame"]

    shots = frames[frame_index]["shots"]

    shot_symbol = convert_shot_symbol(shots, knocked_count, frame_index)
    shots.append(shot_symbol)

    new_frame_index, reset_pins = advance_frame_for_frames(frames, frame_index, shot_symbol)

    if STATE.mode == "baker":
        STATE.current_frame = new_frame_index
    else:
        bowler_state["current_frame"] = new_frame_index

    if reset_pins:
        STATE.standing_pins = set(range(1, 11))

    return {"ok": True}


# ---------------------------------------------------------
# Undo Endpoint
# ---------------------------------------------------------
@app.post("/api/undo")
async def undo():
    restored = STATE.restore_snapshot()
    return {"ok": restored}


@app.post("/api/reset")
async def reset():
    STATE.reset()
    return {"ok": True, "mode": STATE.mode}


@app.get("/api/state")
async def get_state():
    if STATE.mode == "baker":
        total = score_game(STATE.frames)
        bowlers_data = {}
    else:
        total = 0
        bowlers_data = {}
        for bowler_id, bstate in STATE.bowlers.items():
            frames = bstate["frames"]
            bowler_total = score_game(frames)
            bowlers_data[bowler_id] = {
                "frames": frames,
                "total": bowler_total,
                "current_frame": bstate["current_frame"],
            }
            total += bowler_total

    return {
        "mode": STATE.mode,
        "frames": STATE.frames,
        "total": total,
        "standing_pins": list(STATE.standing_pins),
        "bowlers": bowlers_data,
        "active_bowler": STATE.active_bowler,
    }
