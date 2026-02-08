from typing import List, Dict
import copy

def make_empty_frames():
    return [{"shots": [], "score": None} for _ in range(10)]

class BowlingState:
    def __init__(self):
        self.reset()

    def reset(self):
        # Game mode
        self.mode = "baker"

        # Baker mode state
        self.frames: List[dict] = make_empty_frames()
        self.current_frame = 0

        # Peterson mode state
        self.bowlers: Dict[str, dict] = {
            bowler_id: {
                "frames": make_empty_frames(),
                "current_frame": 0
            }
            for bowler_id in ["A", "B", "C", "D", "E"]
        }

        # Active bowler
        self.active_bowler = "A"

        # Standing pins
        self.standing_pins = set(range(1, 11))

        # History stack for Undo
        self.history = []

    # ---------------------------------------------------------
    # Snapshot save/restore
    # ---------------------------------------------------------
    def save_snapshot(self):
        snapshot = {
            "mode": self.mode,
            "frames": copy.deepcopy(self.frames),
            "current_frame": self.current_frame,
            "bowlers": copy.deepcopy(self.bowlers),
            "active_bowler": self.active_bowler,
            "standing_pins": copy.deepcopy(self.standing_pins)
        }
        self.history.append(snapshot)

    def restore_snapshot(self):
        if not self.history:
            return False

        snapshot = self.history.pop()

        self.mode = snapshot["mode"]
        self.frames = snapshot["frames"]
        self.current_frame = snapshot["current_frame"]
        self.bowlers = snapshot["bowlers"]
        self.active_bowler = snapshot["active_bowler"]
        self.standing_pins = snapshot["standing_pins"]

        return True


STATE = BowlingState()
