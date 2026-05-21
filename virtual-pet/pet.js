const STORAGE_KEY = "codexDollPet.v2";
const petSettings = window.CODEX_PET_SETTINGS;
const activePet = petSettings?.pets?.[petSettings.activePetId] ?? {
  name: "Codex",
  asset: "assets/codex_doll_four_modes.png",
  displaySize: "16cm",
  minDisplaySize: "10cm",
};

const defaults = {
  name: activePet.name,
  focus: 86,
  mood: 88,
  energy: 78,
  progress: 0,
  mode: "idle",
  logs: ["玩偶已放进状态台，点一下就能切换系统状态。"],
  lastSeen: Date.now(),
};

const modes = {
  idle: {
    label: "待命",
    log: "切换到待命：玩偶乖乖坐好，等你开口。",
    talk: "我在这里，点一下就开始陪你处理任务。",
    stats: { focus: 2, mood: 3, energy: 5, progress: -4 },
  },
  thinking: {
    label: "思考",
    log: "切换到思考：开始整理线索和下一步。",
    talk: "我在想，把关键点抓住再动手。",
    stats: { focus: 10, mood: 1, energy: -4, progress: 8 },
  },
  working: {
    label: "工作中",
    log: "切换到工作中：进入执行状态。",
    talk: "我开始干活了，先把能落地的部分推进。",
    stats: { focus: 8, mood: 2, energy: -7, progress: 16 },
  },
  done: {
    label: "完成",
    log: "切换到完成：任务收好，玩偶抱着花休息。",
    talk: "完成啦，我把状态放稳了，你可以直接用。",
    stats: { focus: 3, mood: 10, energy: 7, progress: 100 },
  },
};

const modeOrder = Object.keys(modes);
const state = loadState();

const els = {
  petName: document.querySelector("#petName"),
  petAvatar: document.querySelector("#petAvatar"),
  activePetName: document.querySelector("#activePetName"),
  petTalk: document.querySelector("#petTalk"),
  petSize: document.querySelector("#petSize"),
  memoryLog: document.querySelector("#memoryLog"),
  bars: {
    focus: document.querySelector("#focusBar"),
    mood: document.querySelector("#moodBar"),
    energy: document.querySelector("#energyBar"),
    progress: document.querySelector("#progressBar"),
  },
  text: {
    focus: document.querySelector("#focusText"),
    mood: document.querySelector("#moodText"),
    energy: document.querySelector("#energyText"),
    progress: document.querySelector("#progressText"),
  },
};

applyTimeDrift();
applyPetSettings();
render();

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.action, true));
});

document.querySelectorAll("[data-mode]").forEach((button) => {
  if (button.id === "petAvatar") return;
  button.addEventListener("click", () => setMode(button.dataset.mode, true));
});

els.petAvatar.addEventListener("click", () => {
  const nextIndex = (modeOrder.indexOf(state.mode) + 1) % modeOrder.length;
  setMode(modeOrder[nextIndex], true);
  bouncePet();
});

els.petName.addEventListener("input", () => {
  state.name = els.petName.value.trim() || defaults.name;
  saveState();
  renderTalk();
});

window.addEventListener("beforeunload", () => {
  state.lastSeen = Date.now();
  saveState();
});

window.addEventListener("resize", renderPetSize);

function applyPetSettings() {
  document.documentElement.style.setProperty("--doll-size", activePet.displaySize);
  document.documentElement.style.setProperty("--doll-min-size", activePet.minDisplaySize);
  els.petAvatar.style.backgroundImage = `url("${activePet.asset}")`;
  if (els.activePetName) els.activePetName.textContent = activePet.name;
}

function setMode(mode, fromUser) {
  if (!modes[mode]) return;

  state.mode = mode;
  if (fromUser) {
    applyModeStats(modes[mode].stats);
    addLog(modes[mode].log);
    speak(modes[mode].talk);
    bouncePet();
  }

  saveState();
  render();
}

function render() {
  els.petName.value = state.name;
  els.petAvatar.dataset.mode = state.mode;
  els.petAvatar.setAttribute("aria-label", `点按${state.name}玩偶，当前状态：${modes[state.mode].label}`);

  ["focus", "mood", "energy", "progress"].forEach((key) => {
    const value = Math.round(state[key]);
    els.bars[key].style.width = `${value}%`;
    els.text[key].textContent = value;
  });

  document.querySelectorAll("[data-action]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.action === state.mode);
  });

  document.querySelectorAll(".mode-switch button").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.mode === state.mode));
  });

  els.memoryLog.innerHTML = "";
  state.logs.slice(0, 8).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    els.memoryLog.append(li);
  });

  renderTalk();
  renderPetSize();
}

function renderTalk() {
  if (state.energy < 20) {
    speak(`${state.name}有点累，切到待命或完成状态能恢复一点。`, false);
    return;
  }

  if (state.focus < 24) {
    speak(`${state.name}正在重新聚焦，适合先切到思考。`, false);
    return;
  }

  speak(`${state.name}：${modes[state.mode].talk}`, false);
}

function renderPetSize() {
  const size = activePet.displaySize.replace("cm", ".0 cm");
  els.petSize.textContent = `${size} x ${size}`;
}

function speak(text, animate = true) {
  els.petTalk.textContent = text;
  if (!animate) return;

  els.petTalk.animate(
    [
      { transform: "translateY(4px)", opacity: 0.72 },
      { transform: "translateY(0)", opacity: 1 },
    ],
    { duration: 180, easing: "ease-out" },
  );
}

function bouncePet() {
  els.petAvatar.classList.remove("is-happy");
  window.requestAnimationFrame(() => {
    els.petAvatar.classList.add("is-happy");
  });
}

function applyModeStats(stats) {
  Object.entries(stats).forEach(([key, amount]) => {
    if (key === "progress" && amount === 100) {
      state.progress = 100;
      return;
    }
    state[key] = clamp(state[key] + amount);
  });
}

function addLog(text) {
  state.logs.unshift(text);
  state.logs = state.logs.slice(0, 16);
}

function applyTimeDrift() {
  const elapsedMinutes = Math.max(0, (Date.now() - state.lastSeen) / 60000);
  if (elapsedMinutes < 1) return;

  const drift = Math.min(14, elapsedMinutes * 0.1);
  state.focus = clamp(state.focus - drift * 0.4);
  state.mood = clamp(state.mood - drift * 0.25);
  state.energy = clamp(state.energy - drift * 0.55);
  state.lastSeen = Date.now();
  saveState();
}

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return { ...defaults, ...saved };
  } catch {
    return { ...defaults };
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function clamp(value) {
  return Math.max(0, Math.min(100, value));
}
