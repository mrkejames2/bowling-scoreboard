let selectedPins = new Set();
let standingPins = new Set([1,2,3,4,5,6,7,8,9,10]);
let ball = 1;

let currentMode = "baker";
let currentBowler = "A";

function nextBowler(b) {
  const order = { A: "B", B: "C", C: "D", D: "E", E: "A" };
  return order[b] || "A";
}

function tenthFrameComplete(frames) {
  const f = frames[9];
  if (!f) return false;
  const s = f.shots;
  if (s.length === 3) return true;
  if (s.length === 2 && s[0] !== "X" && s[1] !== "/") return true;
  return false;
}

// ---------------------------------------------------------
// Pins rendering
// ---------------------------------------------------------
function renderPins() {
  const container = document.getElementById("pins");
  container.innerHTML = "";

  const rows = [
    [7, 8, 9, 10],
    [4, 5, 6],
    [2, 3],
    [1]
  ];

  rows.forEach(row => {
    const rowDiv = document.createElement("div");
    rowDiv.className = "pin-row";

    row.forEach(pin => {
      const div = document.createElement("div");
      div.className = "pin";
      div.innerText = pin;

      if (!standingPins.has(pin)) {
        div.classList.add("disabled");
      }

      if (standingPins.has(pin)) {
        div.onclick = () => {
          if (selectedPins.has(pin)) {
            selectedPins.delete(pin);
          } else {
            selectedPins.add(pin);
          }
          div.classList.toggle("active-pin");
        };
      }

      rowDiv.appendChild(div);
    });

    container.appendChild(rowDiv);
  });
}

// ---------------------------------------------------------
// Mode switching
// ---------------------------------------------------------
async function changeMode(mode) {
  currentMode = mode;
  await fetch("/api/set_mode", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ mode })
  });

  standingPins = new Set([1,2,3,4,5,6,7,8,9,10]);
  selectedPins.clear();
  ball = 1;

  document.getElementById("bowler-selector").style.display =
    mode === "peterson" ? "block" : "none";

  renderPins();
  renderScorecard();
}

// ---------------------------------------------------------
// Bowler selection
// ---------------------------------------------------------
async function setBowler(bowler) {
  currentBowler = bowler;

  await fetch("/api/set_active_bowler", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ bowler })
  });

  ["A","B","C","D","E"].forEach(id => {
    const btn = document.getElementById(`bowler-${id}`);
    if (!btn) return;
    btn.classList.toggle("active", id === bowler);
  });

  renderScorecard();
}

// ---------------------------------------------------------
// Submit pins
// ---------------------------------------------------------
async function submitPins() {
  const beforeState = await fetch("/api/state").then(r => r.json());
  const beforeFrame = currentMode === "peterson"
    ? beforeState.bowlers[currentBowler].current_frame
    : beforeState.current_frame;

  const standing = Array.from(selectedPins);
  const knockedDown = [...standingPins].filter(p => !standing.includes(p));

  const payload = {
    standing_pins: standing,
    knocked_pins: knockedDown
  };
  if (currentMode === "peterson") {
    payload.bowler = currentBowler;
  }

  await fetch("/api/shot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  standingPins = new Set(standing);
  selectedPins.clear();

  ball++;
  if (ball > 2 && currentMode === "baker") {
    ball = 1;
    standingPins = new Set([1,2,3,4,5,6,7,8,9,10]);
  }

  renderPins();
  await renderScorecard();

  const afterState = await fetch("/api/state").then(r => r.json());
  const afterFrame = currentMode === "peterson"
    ? afterState.bowlers[currentBowler].current_frame
    : afterState.current_frame;

  if (currentMode === "peterson") {
    const frames = afterState.bowlers[currentBowler].frames;
    const frameChanged = afterFrame > beforeFrame;
    const tenthDone = afterFrame === 9 && tenthFrameComplete(frames);

    if (frameChanged || tenthDone) {
      setBowler(nextBowler(currentBowler));
    }
  }
}

// ---------------------------------------------------------
// Strike
// ---------------------------------------------------------
async function sendStrike() {
  const beforeState = await fetch("/api/state").then(r => r.json());
  const beforeFrame = currentMode === "peterson"
    ? beforeState.bowlers[currentBowler].current_frame
    : beforeState.current_frame;

  const knockedDown = Array.from(standingPins);

  const payload = {
    standing_pins: [],
    knocked_pins: knockedDown
  };
  if (currentMode === "peterson") {
    payload.bowler = currentBowler;
  }

  await fetch("/api/shot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  standingPins = new Set([1,2,3,4,5,6,7,8,9,10]);
  selectedPins.clear();
  ball = 1;

  renderPins();
  await renderScorecard();

  const afterState = await fetch("/api/state").then(r => r.json());
  const afterFrame = currentMode === "peterson"
    ? afterState.bowlers[currentBowler].current_frame
    : afterState.current_frame;

  if (currentMode === "peterson") {
    const frames = afterState.bowlers[currentBowler].frames;
    const frameChanged = afterFrame > beforeFrame;
    const tenthDone = afterFrame === 9 && tenthFrameComplete(frames);

    if (frameChanged || tenthDone) {
      setBowler(nextBowler(currentBowler));
    }
  }
}

// ---------------------------------------------------------
// Spare
// ---------------------------------------------------------
async function sendSpare() {
  const beforeState = await fetch("/api/state").then(r => r.json());
  const beforeFrame = currentMode === "peterson"
    ? beforeState.bowlers[currentBowler].current_frame
    : beforeState.current_frame;

  const knockedDown = Array.from(standingPins);

  const payload = {
    standing_pins: [],
    knocked_pins: knockedDown
  };
  if (currentMode === "peterson") {
    payload.bowler = currentBowler;
  }

  await fetch("/api/shot", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  standingPins = new Set([1,2,3,4,5,6,7,8,9,10]);
  selectedPins.clear();
  ball = 1;

  renderPins();
  await renderScorecard();

  const afterState = await fetch("/api/state").then(r => r.json());
  const afterFrame = currentMode === "peterson"
    ? afterState.bowlers[currentBowler].current_frame
    : afterState.current_frame;

  if (currentMode === "peterson") {
    const frames = afterState.bowlers[currentBowler].frames;
    const frameChanged = afterFrame > beforeFrame;
    const tenthDone = afterFrame === 9 && tenthFrameComplete(frames);

    if (frameChanged || tenthDone) {
      setBowler(nextBowler(currentBowler));
    }
  }
}

// ---------------------------------------------------------
// Undo last shot
// ---------------------------------------------------------
async function undoLastShot() {
  await fetch("/api/undo", { method: "POST" });

  const state = await fetch("/api/state").then(r => r.json());

  currentMode = state.mode;
  currentBowler = state.active_bowler;

  standingPins = new Set(state.standing_pins);
  selectedPins.clear();

  ["A","B","C","D","E"].forEach(id => {
    const btn = document.getElementById(`bowler-${id}`);
    if (!btn) return;
    btn.classList.toggle("active", id === currentBowler);
  });

  renderPins();
  renderScorecard();
}

// ---------------------------------------------------------
// Reset game
// ---------------------------------------------------------
async function resetGame() {
  await fetch("/api/reset", { method: "POST" });

  standingPins = new Set([1,2,3,4,5,6,7,8,9,10]);
  selectedPins.clear();
  ball = 1;
  currentMode = "baker";
  currentBowler = "A";

  const bakerRadio = document.querySelector('input[name="mode"][value="baker"]');
  const petersonRadio = document.querySelector('input[name="mode"][value="peterson"]');
  if (bakerRadio) bakerRadio.checked = true;
  if (petersonRadio) petersonRadio.checked = false;

  document.getElementById("bowler-selector").style.display = "none";

  renderPins();
  renderScorecard();
}

// ---------------------------------------------------------
// Highlight current frame
// ---------------------------------------------------------
function highlightCurrentFrame(frames) {
  let currentFrame = frames.findIndex((f, i) => {
    if (f.shots.length === 0) return true;
    if (i < 9) {
      if (f.shots.length === 1 && f.shots[0] !== "X") return true;
      return false;
    } else {
      return f.shots.length < 3;
    }
  });
  if (currentFrame === -1) currentFrame = 9;
  return currentFrame;
}

// ---------------------------------------------------------
// Render scorecard
// ---------------------------------------------------------
async function renderScorecard() {
  const res = await fetch("/api/state");
  const data = await res.json();

  currentMode = data.mode;
  const card = document.getElementById("scorecard");
  card.innerHTML = "";

  document.getElementById("bowler-selector").style.display =
    currentMode === "peterson" ? "block" : "none";

  if (currentMode === "baker") {
    const frames = data.frames;
    const currentFrame = highlightCurrentFrame(frames);

    const block = document.createElement("div");
    block.className = "bowler-block";

    const title = document.createElement("div");
    title.className = "bowler-title";
    title.innerText = "Team (Baker)";
    block.appendChild(title);

    const row = document.createElement("div");
    row.className = "frames-row";

    frames.forEach((f, i) => {
      const box = document.createElement("div");
      box.className = "frame-box";
      if (i === currentFrame) box.classList.add("current");

      const num = document.createElement("div");
      num.className = "frame-number";
      num.innerText = `Frame ${i + 1}`;

      const shots = document.createElement("div");
      shots.className = "shots";
      const displayShots = f.shots.map(s => s === 0 ? "-" : s);
      shots.innerText = displayShots.join(" ");

      const subtotal = document.createElement("div");
      subtotal.className = "frame-total";
      subtotal.innerText = f.score ?? "";

      box.appendChild(num);
      box.appendChild(shots);
      box.appendChild(subtotal);

      row.appendChild(box);
    });

    block.appendChild(row);
    card.appendChild(block);
  } else {
    const bowlers = data.bowlers || {};
    ["A","B","C","D","E"].forEach(id => {
      const b = bowlers[id];
      if (!b) return;

      const frames = b.frames;
      const currentFrame = highlightCurrentFrame(frames);

      const block = document.createElement("div");
      block.className = "bowler-block";

      const title = document.createElement("div");
      title.className = "bowler-title";
      title.innerText = `Bowler ${id} (Total: ${b.total ?? 0})`;
      block.appendChild(title);

      const row = document.createElement("div");
      row.className = "frames-row";

      frames.forEach((f, i) => {
        const box = document.createElement("div");
        box.className = "frame-box";
        if (i === currentFrame) box.classList.add("current");

        const num = document.createElement("div");
        num.className = "frame-number";
        num.innerText = `F${i + 1}`;

        const shots = document.createElement("div");
        shots.className = "shots";
        const displayShots = f.shots.map(s => s === 0 ? "-" : s);
        shots.innerText = displayShots.join(" ");

        const subtotal = document.createElement("div");
        subtotal.className = "frame-total";
        subtotal.innerText = f.score ?? "";

        box.appendChild(num);
        box.appendChild(shots);
        box.appendChild(subtotal);

        row.appendChild(box);
      });

      block.appendChild(row);
      card.appendChild(block);
    });
  }
}

// ---------------------------------------------------------
// Init
// ---------------------------------------------------------
window.onload = async () => {
  const res = await fetch("/api/state");
  const data = await res.json();
  currentMode = data.mode || "baker";
  currentBowler = data.active_bowler || "A";

  const bakerRadio = document.querySelector('input[name="mode"][value="baker"]');
  const petersonRadio = document.querySelector('input[name="mode"][value="peterson"]');
  if (bakerRadio && petersonRadio) {
    if (currentMode === "baker") {
      bakerRadio.checked = true;
      petersonRadio.checked = false;
    } else {
      bakerRadio.checked = false;
      petersonRadio.checked = true;
    }
  }

  document.getElementById("bowler-selector").style.display =
    currentMode === "peterson" ? "block" : "none";

  ["A","B","C","D","E"].forEach(id => {
    const btn = document.getElementById(`bowler-${id}`);
    if (!btn) return;
    btn.classList.toggle("active", id === currentBowler);
  });

  renderPins();
  renderScorecard();
};
