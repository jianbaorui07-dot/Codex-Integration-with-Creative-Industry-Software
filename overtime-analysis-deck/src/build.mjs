import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const runtimeNodeModules = path.join(
  process.env.USERPROFILE || process.env.HOME || "",
  ".cache",
  "codex-runtimes",
  "codex-primary-runtime",
  "dependencies",
  "node",
  "node_modules",
);
const runtimeRequire = createRequire(path.join(runtimeNodeModules, "runtime.cjs"));
const JSZip = runtimeRequire("jszip");

const {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  panel,
  text,
  shape,
  rule,
  fill,
  hug,
  fixed,
  wrap,
  grow,
  fr,
  auto,
} = await import("@oai/artifact-tool");
const { paint, stroke } = await import("@oai/artifact-tool/presentation-jsx");

const ROOT = path.resolve(".");
const OUT = path.join(ROOT, "output");
const SCRATCH = path.join(ROOT, "scratch");
const PREVIEWS = path.join(SCRATCH, "previews");
const PPTX_RENDERS = path.join(SCRATCH, "pptx-renders");
const LAYOUTS = path.join(SCRATCH, "layouts");
const REPORTS = path.join(SCRATCH, "reports");

const W = 1920;
const H = 1080;

const C = {
  ink: "#121416",
  near: "#1F2428",
  paper: "#F5F7F8",
  white: "#FFFFFF",
  quiet: "#65717A",
  rule: "#D6DCE1",
  red: "#F04D4D",
  blue: "#2563EB",
  mint: "#28A875",
  amber: "#F2B84B",
  violet: "#7C3AED",
};

const font = "Microsoft YaHei";

const base = {
  typeface: font,
  color: C.ink,
};

function t(value, opts = {}) {
  return text(value, {
    width: opts.width ?? fill,
    height: opts.height ?? hug,
    name: opts.name,
    columnSpan: opts.columnSpan,
    rowSpan: opts.rowSpan,
    style: {
      ...base,
      ...opts.style,
    },
  });
}

function bg(fillColor = C.paper) {
  return shape({
    name: "slide-background",
    width: fill,
    height: fill,
    fill: paint(fillColor),
    line: stroke("none"),
  });
}

function accentBar(color = C.red, width = 170) {
  return rule({
    name: "accent-rule",
    width: fixed(width),
    weight: 8,
    stroke: color,
  });
}

function safeRoot(children, options = {}) {
  return column(
    {
      name: "content-root",
      width: fill,
      height: fill,
      padding: options.padding ?? { x: 96, y: 72 },
      gap: options.gap ?? 34,
      justify: options.justify ?? "start",
    },
    children,
  );
}

function slideWith(content, background = C.paper) {
  const slide = deck.slides.add();
  slide.compose(
    layers(
      { name: "slide-layers", width: fill, height: fill },
      [bg(background), content],
    ),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
  return slide;
}

function label(value, color = C.quiet, name) {
  return t(value, {
    name,
    width: hug,
    style: {
      fontSize: 21,
      bold: true,
      color,
      letterSpacing: 0,
    },
  });
}

function openMetric(num, caption, color, name) {
  return column(
    { name, width: fill, height: hug, gap: 12 },
    [
      t(num, {
        name: `${name}-num`,
        width: fill,
        style: {
          fontSize: 95,
          bold: true,
          color,
          lineSpacing: 0.95,
        },
      }),
      t(caption, {
        name: `${name}-caption`,
        width: fill,
        style: { fontSize: 25, color: C.near, lineSpacing: 1.18 },
      }),
    ],
  );
}

function sectionHeader(kicker, title, subtitle, color = C.red) {
  return column(
    { name: "title-stack", width: fill, height: hug, gap: 18 },
    [
      row(
        { name: "kicker-row", width: fill, height: hug, gap: 18, align: "center" },
        [accentBar(color, 112), label(kicker, color, "slide-kicker")],
      ),
      t(title, {
        name: "slide-title",
        width: wrap(1280),
        style: {
          fontSize: 64,
          bold: true,
          color: C.ink,
          lineSpacing: 1.04,
        },
      }),
      subtitle
        ? t(subtitle, {
            name: "slide-subtitle",
            width: wrap(1180),
            style: {
              fontSize: 27,
              color: C.quiet,
              lineSpacing: 1.25,
            },
          })
        : null,
    ].filter(Boolean),
  );
}

function timelineItem(mark, title, body, color, name) {
  return column(
    { name, width: fill, height: hug, gap: 12 },
    [
      t(mark, {
        name: `${name}-mark`,
        width: fill,
        style: { fontSize: 31, bold: true, color },
      }),
      rule({ name: `${name}-rule`, width: fill, weight: 4, stroke: color }),
      t(title, {
        name: `${name}-title`,
        width: fill,
        style: { fontSize: 32, bold: true, color: C.ink, lineSpacing: 1.12 },
      }),
      t(body, {
        name: `${name}-body`,
        width: fill,
        style: { fontSize: 24, color: C.near, lineSpacing: 1.28 },
      }),
    ],
  );
}

function comparisonRow(left, right, color, name) {
  return grid(
    {
      name,
      width: fill,
      height: hug,
      columns: [fr(0.88), fr(0.1), fr(1.12)],
      columnGap: 24,
      alignItems: "center",
    },
    [
      t(left, {
        name: `${name}-left`,
        width: fill,
        style: { fontSize: 25, color: C.quiet, lineSpacing: 1.2 },
      }),
      t("→", {
        name: `${name}-arrow`,
        width: fill,
        style: { fontSize: 32, bold: true, color },
      }),
      t(right, {
        name: `${name}-right`,
        width: fill,
        style: { fontSize: 29, bold: true, color: C.ink, lineSpacing: 1.18 },
      }),
    ],
  );
}

async function resetDirs() {
  await fs.rm(OUT, { recursive: true, force: true });
  await fs.rm(PREVIEWS, { recursive: true, force: true });
  await fs.rm(PPTX_RENDERS, { recursive: true, force: true });
  await fs.rm(LAYOUTS, { recursive: true, force: true });
  await fs.rm(REPORTS, { recursive: true, force: true });
  await fs.mkdir(OUT, { recursive: true });
  await fs.mkdir(PREVIEWS, { recursive: true });
  await fs.mkdir(PPTX_RENDERS, { recursive: true });
  await fs.mkdir(LAYOUTS, { recursive: true });
  await fs.mkdir(REPORTS, { recursive: true });
}

async function saveBlob(blob, filePath) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  if (typeof blob.save === "function") {
    await blob.save(filePath);
    return;
  }
  const buf = Buffer.from(await blob.arrayBuffer());
  await fs.writeFile(filePath, buf);
}

const deck = Presentation.create({
  slideSize: { width: W, height: H },
});

// 1. Cover: dedicated editorial poster, not the content slide shell.
slideWith(
  layers(
    { name: "cover-stack", width: fill, height: fill },
    [
      bg(C.ink),
      column(
        {
          name: "cover-content",
          width: fill,
          height: fill,
          padding: { x: 112, y: 76 },
          justify: "between",
        },
        [
          row(
            { name: "cover-top", width: fill, height: hug, justify: "between", align: "center" },
            [
              label("问题分析 / 沟通方案", C.red, "cover-kicker"),
              t("例外不能变成默认", {
                name: "cover-context",
                width: hug,
                style: { fontSize: 22, color: "#D9E0E6" },
              }),
            ],
          ),
          column(
            { name: "cover-title-stack", width: fill, height: hug, gap: 26 },
            [
              t("21:30", {
                name: "cover-time",
                width: fill,
                style: {
                  fontSize: 214,
                  bold: true,
                  color: C.red,
                  lineSpacing: 0.88,
                },
              }),
              t("加班不是努力的同义词", {
                name: "cover-title",
                width: wrap(1300),
                style: {
                  fontSize: 76,
                  bold: true,
                  color: C.white,
                  lineSpacing: 1.05,
                },
              }),
              t("它更像一个系统信号：容量、流程、边界、激励里，至少有一处正在失衡。", {
                name: "cover-subtitle",
                width: wrap(1120),
                style: {
                  fontSize: 30,
                  color: "#D9E0E6",
                  lineSpacing: 1.22,
                },
              }),
            ],
          ),
          row(
            { name: "cover-bottom", width: fill, height: hug, gap: 18, align: "center" },
            [
              rule({ name: "cover-bottom-line", width: fixed(540), weight: 3, stroke: "#55606A" }),
              t("分析让我加班这个问题", {
                name: "cover-footer",
                width: hug,
                style: { fontSize: 18, color: "#B9C3CB" },
              }),
            ],
          ),
        ],
      ),
    ],
  ),
  C.ink,
);

// 2. Reframe.
slideWith(
  safeRoot(
    [
      sectionHeader(
        "01 / 先换个名字",
        "这不是“我不想干”，而是容量失衡",
        "加班常被包装成态度问题；真正该问的是：工作量、优先级和交付承诺是否仍然匹配。",
        C.blue,
      ),
      row(
        { name: "reframe-body", width: fill, height: fill, gap: 64, align: "center" },
        [
          column(
            { name: "reframe-left", width: grow(1), height: hug, gap: 16 },
            [
              t("当“临时任务”越来越像固定班次，问题就已经不在某一天晚上。", {
                name: "reframe-big-claim",
                width: wrap(760),
                style: { fontSize: 58, bold: true, color: C.ink, lineSpacing: 1.08 },
              }),
              t("先把争论从“谁够不够拼”拉回“系统如何运转”。", {
                name: "reframe-note",
                width: wrap(680),
                style: { fontSize: 27, color: C.quiet, lineSpacing: 1.25 },
              }),
            ],
          ),
          column(
            { name: "reframe-signals", width: grow(0.86), height: hug, gap: 30 },
            [
              openMetric("任务", "总是晚上才变成“今天必须要”", C.red, "signal-1"),
              openMetric("边界", "下班时间默认可被占用", C.amber, "signal-2"),
              openMetric("反馈", "救火被奖励，规划被忽视", C.mint, "signal-3"),
            ],
          ),
        ],
      ),
    ],
    { gap: 46 },
  ),
);

// 3. Root causes matrix.
slideWith(
  safeRoot(
    [
      sectionHeader(
        "02 / 找根因",
        "加班通常不是一个原因，而是四层问题叠在一起",
        "别急着只谈情绪。先分清：是需求超载、流程漏水、边界模糊，还是激励扭曲。",
        C.red,
      ),
      grid(
        {
          name: "root-cause-matrix",
          width: fill,
          height: fill,
          columns: [fr(1), fr(1)],
          rows: [fr(1), fr(1)],
          columnGap: 44,
          rowGap: 34,
          padding: { top: 10 },
        },
        [
          column(
            { name: "cause-demand", width: fill, height: fill, gap: 16 },
            [
              label("需求超载", C.red, "cause-demand-label"),
              t("承诺量大于真实容量", {
                name: "cause-demand-title",
                width: fill,
                style: { fontSize: 38, bold: true, color: C.ink },
              }),
              t("表现：排期永远乐观；重要任务和临时任务抢同一块时间。", {
                name: "cause-demand-body",
                width: fill,
                style: { fontSize: 25, color: C.near, lineSpacing: 1.25 },
              }),
              rule({ name: "cause-demand-rule", width: fill, weight: 3, stroke: C.red }),
            ],
          ),
          column(
            { name: "cause-process", width: fill, height: fill, gap: 16 },
            [
              label("流程漏水", C.blue, "cause-process-label"),
              t("白天没解决，晚上才补洞", {
                name: "cause-process-title",
                width: fill,
                style: { fontSize: 38, bold: true, color: C.ink },
              }),
              t("表现：需求变更、等待审批、会议打断，把深度工作挤到下班后。", {
                name: "cause-process-body",
                width: fill,
                style: { fontSize: 25, color: C.near, lineSpacing: 1.25 },
              }),
              rule({ name: "cause-process-rule", width: fill, weight: 3, stroke: C.blue }),
            ],
          ),
          column(
            { name: "cause-boundary", width: fill, height: fill, gap: 16 },
            [
              label("边界模糊", C.amber, "cause-boundary-label"),
              t("“能不能帮一下”没有出口", {
                name: "cause-boundary-title",
                width: fill,
                style: { fontSize: 38, bold: true, color: C.ink },
              }),
              t("表现：谁都可以插队；拒绝成本很高；紧急和重要混在一起。", {
                name: "cause-boundary-body",
                width: fill,
                style: { fontSize: 25, color: C.near, lineSpacing: 1.25 },
              }),
              rule({ name: "cause-boundary-rule", width: fill, weight: 3, stroke: C.amber }),
            ],
          ),
          column(
            { name: "cause-incentive", width: fill, height: fill, gap: 16 },
            [
              label("激励扭曲", C.mint, "cause-incentive-label"),
              t("救火比预防更容易被看见", {
                name: "cause-incentive-title",
                width: fill,
                style: { fontSize: 38, bold: true, color: C.ink },
              }),
              t("表现：加班被当作忠诚度；准时交付反而显得“不够拼”。", {
                name: "cause-incentive-body",
                width: fill,
                style: { fontSize: 25, color: C.near, lineSpacing: 1.25 },
              }),
              rule({ name: "cause-incentive-rule", width: fill, weight: 3, stroke: C.mint }),
            ],
          ),
        ],
      ),
    ],
    { gap: 42 },
  ),
);

// 4. Self-reinforcing loop.
slideWith(
  safeRoot(
    [
      sectionHeader(
        "03 / 看代价",
        "最危险的不是多干两小时，而是加班会自我复制",
        "疲劳带来错误，错误带来返工，返工又吃掉下一天的正常工作时间。",
        C.violet,
      ),
      row(
        { name: "loop-stage", width: fill, height: fill, gap: 34, align: "center" },
        [
          column(
            { name: "loop-left", width: grow(0.95), height: hug, gap: 22 },
            [
              t("晚下班", {
                name: "loop-late-title",
                width: fill,
                style: { fontSize: 76, bold: true, color: C.red, lineSpacing: 1 },
              }),
              t("看起来解决了今天的问题。", {
                name: "loop-late-sub",
                width: fill,
                style: { fontSize: 29, color: C.quiet },
              }),
            ],
          ),
          column(
            { name: "loop-chain", width: grow(1.25), height: hug, gap: 22 },
            [
              comparisonRow("疲劳上升", "判断力下降", C.red, "loop-row-1"),
              comparisonRow("判断力下降", "返工和沟通成本增加", C.amber, "loop-row-2"),
              comparisonRow("返工增加", "第二天可用容量变少", C.blue, "loop-row-3"),
              comparisonRow("容量变少", "新的加班更容易发生", C.violet, "loop-row-4"),
            ],
          ),
          column(
            { name: "loop-right", width: grow(0.9), height: hug, gap: 22 },
            [
              t("明天更难", {
                name: "loop-tomorrow-title",
                width: fill,
                style: { fontSize: 76, bold: true, color: C.ink, lineSpacing: 1 },
              }),
              t("真正的问题被顺延，并开始滚雪球。", {
                name: "loop-tomorrow-sub",
                width: fill,
                style: { fontSize: 29, color: C.quiet, lineSpacing: 1.22 },
              }),
            ],
          ),
        ],
      ),
    ],
    { gap: 42 },
  ),
);

// 5. Decision filter.
slideWith(
  safeRoot(
    [
      sectionHeader(
        "04 / 判断标准",
        "不是所有加班都一样：先问这三件事",
        "一次偶发救急可以讨论；长期默认占用，需要被重新设计。",
        C.mint,
      ),
      grid(
        {
          name: "three-questions",
          width: fill,
          height: fill,
          columns: [fr(1), fr(1), fr(1)],
          columnGap: 52,
          alignItems: "start",
          padding: { top: 40 },
        },
        [
          column(
            { name: "question-1", width: fill, height: hug, gap: 20 },
            [
              t("1", { name: "q1-num", width: fill, style: { fontSize: 108, bold: true, color: C.red } }),
              t("真的紧急吗", { name: "q1-title", width: fill, style: { fontSize: 42, bold: true } }),
              t("如果明早处理，损失是什么？谁承担？有没有可替代方案？", {
                name: "q1-body",
                width: fill,
                style: { fontSize: 26, color: C.near, lineSpacing: 1.28 },
              }),
            ],
          ),
          column(
            { name: "question-2", width: fill, height: hug, gap: 20 },
            [
              t("2", { name: "q2-num", width: fill, style: { fontSize: 108, bold: true, color: C.blue } }),
              t("谁改变了计划", { name: "q2-title", width: fill, style: { fontSize: 42, bold: true } }),
              t("是原本排期错误，还是新增插队？需要把责任和优先级说清楚。", {
                name: "q2-body",
                width: fill,
                style: { fontSize: 26, color: C.near, lineSpacing: 1.28 },
              }),
            ],
          ),
          column(
            { name: "question-3", width: fill, height: hug, gap: 20 },
            [
              t("3", { name: "q3-num", width: fill, style: { fontSize: 108, bold: true, color: C.mint } }),
              t("边界怎么补偿", { name: "q3-title", width: fill, style: { fontSize: 42, bold: true } }),
              t("今晚多出来的时间，要换来延期、降范围、补休、轮换或明确的下次规则。", {
                name: "q3-body",
                width: fill,
                style: { fontSize: 26, color: C.near, lineSpacing: 1.28 },
              }),
            ],
          ),
        ],
      ),
      t("判断原则：加班如果没有条件、边界和复盘，就会从例外变成制度。", {
        name: "decision-footer",
        width: fill,
        style: { fontSize: 24, color: C.quiet },
      }),
    ],
    { gap: 36 },
  ),
);

// 6. Conversation script.
slideWith(
  safeRoot(
    [
      sectionHeader(
        "05 / 怎么谈",
        "别把谈判开成抱怨；把它开成排优先级",
        "目标不是证明你很累，而是让对方必须在范围、时间、质量之间做选择。",
        C.amber,
      ),
      grid(
        {
          name: "conversation-grid",
          width: fill,
          height: fill,
          columns: [fr(0.92), fixed(3), fr(1.08)],
          columnGap: 46,
          alignItems: "start",
          padding: { top: 20 },
        },
        [
          column(
            { name: "conversation-left", width: fill, height: hug, gap: 28 },
            [
              label("容易陷入的说法", C.red, "conv-left-label"),
              t("“我最近太累了，能不能别再让我加班？”", {
                name: "conv-bad-quote",
                width: fill,
                style: { fontSize: 42, bold: true, color: C.ink, lineSpacing: 1.18 },
              }),
              t("问题：对方可能只听到情绪，没有被迫面对工作系统里的取舍。", {
                name: "conv-bad-note",
                width: fill,
                style: { fontSize: 25, color: C.quiet, lineSpacing: 1.25 },
              }),
            ],
          ),
          shape({
            name: "conversation-divider",
            width: fill,
            height: fill,
            fill: paint(C.rule),
            line: stroke("none"),
          }),
          column(
            { name: "conversation-right", width: fill, height: hug, gap: 28 },
            [
              label("更有效的说法", C.mint, "conv-right-label"),
              t("“这周我已经有 3 个晚上在补临时任务。若今晚继续做 A，B 会延到周五。你希望我优先保哪个？”", {
                name: "conv-good-quote",
                width: fill,
                style: { fontSize: 40, bold: true, color: C.ink, lineSpacing: 1.18 },
              }),
              t("结构：事实记录 → 影响说明 → 选项呈现 → 请求决策。", {
                name: "conv-good-note",
                width: fill,
                style: { fontSize: 26, color: C.near, lineSpacing: 1.25 },
              }),
            ],
          ),
        ],
      ),
    ],
    { gap: 38 },
  ),
);

// 7. Operating fixes.
slideWith(
  safeRoot(
    [
      sectionHeader(
        "06 / 怎么改",
        "把加班从个人忍耐，改成团队治理问题",
        "一次对话解决不了所有事；但可以把“默认加班”的路径逐步堵上。",
        C.blue,
      ),
      grid(
        {
          name: "governance-timeline",
          width: fill,
          height: fill,
          columns: [fr(1), fr(1), fr(1)],
          columnGap: 56,
          alignItems: "start",
          padding: { top: 54 },
        },
        [
          timelineItem(
            "0-7 天",
            "先把事实拉出来",
            "记录工时、任务来源、插队原因、被影响的原计划。没有记录，讨论会回到感受。",
            C.red,
            "timeline-1",
          ),
          timelineItem(
            "2-4 周",
            "建立可执行边界",
            "要求优先级确认、需求冻结窗口、值班轮换、补休或调休安排。",
            C.amber,
            "timeline-2",
          ),
          timelineItem(
            "长期",
            "调整系统容量",
            "如果工作量长期超过人力，需要改范围、改排期、增资源，或重新定义岗位预期。",
            C.mint,
            "timeline-3",
          ),
        ],
      ),
    ],
    { gap: 38 },
  ),
);

// 8. Personal next steps.
slideWith(
  safeRoot(
    [
      row(
        { name: "close-top", width: fill, height: hug, gap: 18, align: "center" },
        [accentBar(C.red, 112), label("07 / 个人下一步", C.red, "close-kicker")],
      ),
      row(
        { name: "close-main", width: fill, height: fill, gap: 76, align: "center" },
        [
          column(
            { name: "close-left", width: grow(1.05), height: hug, gap: 28 },
            [
              t("今晚就做三件事", {
                name: "close-title",
                width: wrap(760),
                style: { fontSize: 78, bold: true, color: C.ink, lineSpacing: 1.03 },
              }),
              t("目标不是马上赢一场争论，而是把问题从“你扛不扛得住”改写成“系统怎么重新分配”。", {
                name: "close-subtitle",
                width: wrap(760),
                style: { fontSize: 29, color: C.quiet, lineSpacing: 1.25 },
              }),
            ],
          ),
          column(
            { name: "close-actions", width: grow(1), height: hug, gap: 34 },
            [
              comparisonRow("1", "补一张过去两周的加班记录", C.red, "action-1"),
              comparisonRow("2", "约 30 分钟谈优先级和边界", C.blue, "action-2"),
              comparisonRow("3", "给出四个选项：延期、降范围、补偿、轮换", C.mint, "action-3"),
              rule({ name: "close-rule", width: fill, weight: 3, stroke: C.rule }),
              t("底线不是态度强硬，而是让每一次额外占用都有原因、有代价、有下次规则。", {
                name: "close-final",
                width: fill,
                style: { fontSize: 30, bold: true, color: C.ink, lineSpacing: 1.22 },
              }),
            ],
          ),
        ],
      ),
      t("注：本 deck 是问题分析和沟通框架，不替代当地劳动规则或专业法律意见。", {
        name: "close-footnote",
        width: fill,
        style: { fontSize: 16, color: C.quiet },
      }),
    ],
    { gap: 38 },
  ),
);

function collectLayoutFailures(layout) {
  const failures = [];
  const slideNo = layout?.slide?.slide ?? "?";
  const elements = layout.elements ?? [];
  for (const el of elements) {
    const name = el.name || el.aid || "unnamed";
    const bbox = el.bbox || el.frame;
    if (bbox) {
      const left = bbox.left ?? bbox.x ?? 0;
      const top = bbox.top ?? bbox.y ?? 0;
      const width = bbox.width ?? 0;
      const height = bbox.height ?? 0;
      if (left < -1 || top < -1 || left + width > W + 1 || top + height > H + 1) {
        failures.push(`slide ${slideNo}: ${name} outside canvas`);
      }
    }
    if (el.textLayout && bbox) {
      const maxLine = Math.max(0, ...(el.textLayout.lines ?? []).map((line) => line.width ?? 0));
      const boxW = bbox.width ?? 0;
      const boxH = bbox.height ?? 0;
      if (el.textLayout.height > boxH + 1) {
        failures.push(`slide ${slideNo}: ${name} text height overflow`);
      }
      if (maxLine > boxW + 1) {
        failures.push(`slide ${slideNo}: ${name} text width overflow`);
      }
    }
  }
  return failures;
}

async function inspectPptxPackage(pptxPath) {
  const buffer = await fs.readFile(pptxPath);
  const zip = await JSZip.loadAsync(buffer);
  const files = Object.keys(zip.files);
  const slideXml = files
    .filter((name) => /^ppt\/slides\/slide\d+\.xml$/.test(name))
    .sort((a, b) => Number(a.match(/slide(\d+)/)[1]) - Number(b.match(/slide(\d+)/)[1]));
  const media = files.filter((name) => name.startsWith("ppt/media/"));
  const failures = [];
  const placeholder = /\b(Slide Number|Click to add|Lorem ipsum|Replace with|TODO|TBD)\b/i;

  if (!slideXml.length) failures.push("PPTX contains no slide XML parts.");
  for (let i = 0; i < slideXml.length; i += 1) {
    const xml = await zip.file(slideXml[i]).async("string");
    if (placeholder.test(xml)) failures.push(`slide ${i + 1}: placeholder/debug text found`);
    if (/\btype="sldNum"|\bplaceholderType: "sldNum"|Slide Number/i.test(xml)) {
      failures.push(`slide ${i + 1}: slide-number placeholder found`);
    }
  }
  for (const file of media) {
    const bytes = await zip.file(file).async("uint8array");
    if (!bytes.length) failures.push(`${file}: zero-byte media`);
  }
  return {
    slide_count: slideXml.length,
    media_count: media.length,
    failures,
  };
}

async function renderDeckSlides(presentation, dir) {
  const paths = [];
  for (let i = 0; i < presentation.slides.count; i += 1) {
    const slide = presentation.slides.getItem(i);
    const pngPath = path.join(dir, `slide-${String(i + 1).padStart(2, "0")}.png`);
    await saveBlob(await slide.export({ format: "png" }), pngPath);
    paths.push(pngPath);
  }
  return paths;
}

async function exportLayouts(presentation) {
  const failures = [];
  const paths = [];
  for (let i = 0; i < presentation.slides.count; i += 1) {
    const slide = presentation.slides.getItem(i);
    const layoutPath = path.join(LAYOUTS, `slide-${String(i + 1).padStart(2, "0")}.layout.json`);
    const blob = await slide.export({ format: "layout" });
    await saveBlob(blob, layoutPath);
    const layout = JSON.parse(await fs.readFile(layoutPath, "utf8"));
    failures.push(...collectLayoutFailures(layout));
    paths.push(layoutPath);
  }
  return { paths, failures };
}

async function main() {
  await resetDirs();

  const pptxPath = path.join(OUT, "output.pptx");
  await saveBlob(await PresentationFile.exportPptx(deck), pptxPath);

  const previewPaths = await renderDeckSlides(deck, PREVIEWS);
  const layoutReport = await exportLayouts(deck);
  const packageReport = await inspectPptxPackage(pptxPath);

  const savedBytes = await fs.readFile(pptxPath);
  const imported = await PresentationFile.importPptx(savedBytes);
  const pptxRenderPaths = await renderDeckSlides(imported, PPTX_RENDERS);

  const report = {
    pptx: pptxPath,
    slide_count: deck.slides.count,
    preview_paths: previewPaths,
    saved_pptx_render_paths: pptxRenderPaths,
    layout_paths: layoutReport.paths,
    layout_failures: layoutReport.failures,
    package_report: packageReport,
    failures: [...layoutReport.failures, ...packageReport.failures],
  };

  await fs.writeFile(path.join(REPORTS, "build-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8");
  if (report.failures.length) {
    console.error(report.failures.join("\n"));
    process.exit(1);
  }
  console.log(JSON.stringify(report, null, 2));
}

await main();
