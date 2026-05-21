const works = [
  {
    title: "红墙之后",
    style: "现代",
    palette: "warm",
    energy: 4,
    meta: "压缩的建筑色块与暖光边界，适合做展览主视觉。",
    tags: ["色域冲突", "城市", "高张力"],
    preview: "linear-gradient(135deg, #b53d32 0 35%, #f3c65d 35% 52%, #263d38 52% 100%)",
    shape: "rgba(255,253,248,.72)",
    shape2: "rgba(36,107,115,.72)",
  },
  {
    title: "雾中山形",
    style: "东方",
    palette: "cool",
    energy: 2,
    meta: "留白、墨色层叠与低饱和青灰，适合安静的空间叙事。",
    tags: ["留白", "山水", "静观"],
    preview: "linear-gradient(160deg, #eef0e8 0 38%, #7aa7a1 38% 57%, #263d38 57% 100%)",
    shape: "rgba(39,46,43,.28)",
    shape2: "rgba(122,167,161,.68)",
  },
  {
    title: "午后切面",
    style: "抽象",
    palette: "warm",
    energy: 5,
    meta: "几何切割与快速笔触形成节奏，可转化为海报或动态开屏。",
    tags: ["几何", "速度", "明亮"],
    preview: "conic-gradient(from 210deg, #ef8354, #f7d96f, #246b73, #1f2523, #ef8354)",
    shape: "rgba(255,253,248,.55)",
    shape2: "rgba(194,78,58,.78)",
  },
  {
    title: "石膏蓝",
    style: "古典",
    palette: "cool",
    energy: 3,
    meta: "雕塑感的冷色光影，用现代构图重新处理古典秩序。",
    tags: ["古典", "光影", "秩序"],
    preview: "radial-gradient(circle at 38% 35%, #f4f0e6 0 20%, #8fa8b7 21% 48%, #2f4538 49% 100%)",
    shape: "rgba(255,255,255,.64)",
    shape2: "rgba(31,37,35,.48)",
  },
  {
    title: "土色档案",
    style: "现代",
    palette: "earth",
    energy: 3,
    meta: "档案纸、陶土与深绿形成克制的材料感，适合品牌图册。",
    tags: ["材料", "档案", "克制"],
    preview: "linear-gradient(145deg, #c7b28a 0 28%, #6e5c3f 28% 49%, #2f4538 49% 100%)",
    shape: "rgba(255,253,248,.42)",
    shape2: "rgba(224,184,77,.56)",
  },
  {
    title: "水面练习",
    style: "东方",
    palette: "cool",
    energy: 1,
    meta: "轻薄的蓝绿色层次，适合做冥想、诗歌或音乐类视觉。",
    tags: ["水面", "低噪声", "呼吸感"],
    preview: "repeating-linear-gradient(170deg, #eef0e8 0 18px, #b9d1cb 18px 34px, #6f9695 34px 48px)",
    shape: "rgba(255,253,248,.52)",
    shape2: "rgba(36,107,115,.42)",
  },
];

const state = {
  style: "all",
  palette: "all",
  minEnergy: 1,
  layers: 10,
  stroke: 38,
  seed: 9,
  selected: works[0],
};

const gallery = document.querySelector("#gallery");
const visibleCount = document.querySelector("#visibleCount");
const moodScore = document.querySelector("#moodScore");
const focusTitle = document.querySelector("#focusTitle");
const focusMeta = document.querySelector("#focusMeta");
const focusTags = document.querySelector("#focusTags");
const canvas = document.querySelector("#artCanvas");
const ctx = canvas.getContext("2d");

function filteredWorks() {
  return works.filter((work) => {
    const styleMatches = state.style === "all" || work.style === state.style;
    const paletteMatches = state.palette === "all" || work.palette === state.palette;
    return styleMatches && paletteMatches && work.energy >= state.minEnergy;
  });
}

function renderGallery() {
  const visible = filteredWorks();
  gallery.innerHTML = "";
  visibleCount.textContent = visible.length;
  moodScore.textContent = visible.length
    ? (visible.reduce((sum, work) => sum + work.energy, 0) / visible.length).toFixed(1)
    : "0";

  visible.forEach((work) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = `art-card${state.selected.title === work.title ? " active" : ""}`;
    card.innerHTML = `
      <span class="art-preview" style="--preview:${work.preview};--shape:${work.shape};--shape-2:${work.shape2}"></span>
      <span>
        <h3>${work.title}</h3>
        <p>${work.style} / 张力 ${work.energy}</p>
      </span>
    `;
    card.addEventListener("click", () => {
      state.selected = work;
      state.seed += work.energy;
      renderFocus();
      renderGallery();
      drawCanvas();
    });
    gallery.appendChild(card);
  });

  if (!visible.includes(state.selected) && visible[0]) {
    state.selected = visible[0];
    renderFocus();
  }
}

function renderFocus() {
  focusTitle.textContent = state.selected.title;
  focusMeta.textContent = state.selected.meta;
  focusTags.innerHTML = state.selected.tags.map((tag) => `<span class="tag">${tag}</span>`).join("");
}

function seededRandom(seed) {
  let value = seed % 2147483647;
  return () => {
    value = (value * 16807) % 2147483647;
    return (value - 1) / 2147483646;
  };
}

function drawCanvas() {
  const random = seededRandom(state.seed + state.layers * 13 + state.stroke);
  const palette = {
    warm: ["#c24e3a", "#ef8354", "#e0b84d", "#fff3d0", "#27322f"],
    cool: ["#246b73", "#7aa7a1", "#c6d9d2", "#f7f4ed", "#243f3c"],
    earth: ["#6e5c3f", "#b19b72", "#d8c7a3", "#2f4538", "#fffdf8"],
    all: ["#c24e3a", "#246b73", "#e0b84d", "#2f4538", "#fffdf8"],
  }[state.selected.palette || state.palette];

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#f4efe4";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < state.layers; i += 1) {
    const color = palette[Math.floor(random() * palette.length)];
    const x = random() * canvas.width;
    const y = random() * canvas.height;
    const width = 130 + random() * 360;
    const height = 60 + random() * 210;
    const rotation = random() * Math.PI;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rotation);
    ctx.globalAlpha = 0.35 + random() * 0.42;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.roundRect(-width / 2, -height / 2, width, height, state.stroke);
    ctx.fill();
    ctx.restore();
  }

  for (let i = 0; i < 34; i += 1) {
    ctx.strokeStyle = palette[Math.floor(random() * palette.length)];
    ctx.globalAlpha = 0.26;
    ctx.lineWidth = 1 + random() * 5;
    ctx.beginPath();
    const startX = random() * canvas.width;
    const startY = random() * canvas.height;
    ctx.moveTo(startX, startY);
    ctx.bezierCurveTo(
      random() * canvas.width,
      random() * canvas.height,
      random() * canvas.width,
      random() * canvas.height,
      random() * canvas.width,
      random() * canvas.height,
    );
    ctx.stroke();
  }

  ctx.globalAlpha = 1;
}

document.querySelector("#styleFilter").addEventListener("change", (event) => {
  state.style = event.target.value;
  renderGallery();
});

document.querySelector("#energyFilter").addEventListener("input", (event) => {
  state.minEnergy = Number(event.target.value);
  renderGallery();
});

document.querySelectorAll(".swatch").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector(".swatch.active").classList.remove("active");
    button.classList.add("active");
    state.palette = button.dataset.palette;
    renderGallery();
  });
});

document.querySelector("#layerControl").addEventListener("input", (event) => {
  state.layers = Number(event.target.value);
  drawCanvas();
});

document.querySelector("#strokeControl").addEventListener("input", (event) => {
  state.stroke = Number(event.target.value);
  drawCanvas();
});

document.querySelector("#shuffleCanvas").addEventListener("click", () => {
  state.seed += 17;
  drawCanvas();
});

document.querySelector("#resetFilters").addEventListener("click", () => {
  state.style = "all";
  state.palette = "all";
  state.minEnergy = 1;
  document.querySelector("#styleFilter").value = "all";
  document.querySelector("#energyFilter").value = "1";
  document.querySelector(".swatch.active").classList.remove("active");
  document.querySelector('[data-palette="all"]').classList.add("active");
  renderGallery();
});

renderFocus();
renderGallery();
drawCanvas();
