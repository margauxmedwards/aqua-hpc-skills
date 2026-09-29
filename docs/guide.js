"use strict";
// Shared by index.html (agent guide) and first-job.html (Aqua basics).
// Each block runs only when its elements are present on the page.
document.documentElement.classList.add("js");

const agents = {
  codex: { label: "Codex", path: ".agents", prefix: "$aqua-hpc" },
  claude: { label: "Claude Code", path: ".claude", prefix: "/aqua-hpc" },
  copilot: {
    label: "Copilot",
    path: ".github",
    prefix: "Use the aqua-hpc skill to",
  },
};
const firstPrompt = document.getElementById("first-prompt");
if (firstPrompt) {
  const basePrompt = firstPrompt.textContent;
  document.querySelectorAll("[data-agent]").forEach((button) =>
    button.addEventListener("click", () => {
      const key = button.dataset.agent,
        a = agents[key];
      document
        .querySelectorAll("[data-agent]")
        .forEach((b) => b.setAttribute("aria-pressed", String(b === button)));
      document.getElementById("agent-label").textContent =
        `Install for ${a.label} · from the toolkit directory`;
      document.getElementById("install-command").textContent =
        `python3 scripts/install_skills.py --agent ${key} --project /path/to/your/project`;
      const location = document.getElementById("agent-location");
      location.replaceChildren();
      location.append("Installed into ");
      const code = document.createElement("code");
      code.textContent = `${a.path}/skills/aqua-hpc`;
      location.append(code, ` in your project. Start or reload ${a.label} there. `);
      location.append(
        key === "copilot"
          ? "Ask it to use the aqua-hpc skill."
          : `Invoke with ${a.prefix}.`,
      );
      firstPrompt.textContent = basePrompt.replace("$aqua-hpc", a.prefix);
    }),
  );
}

document.querySelectorAll("[data-copy]").forEach((button) =>
  button.addEventListener("click", async () => {
    const text = document.getElementById(button.dataset.copy).textContent;
    try {
      if (!navigator.clipboard) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(text);
      document.getElementById("copy-status").textContent =
        "Copied to clipboard.";
      button.textContent = "Copied";
      setTimeout(() => (button.textContent = "Copy"), 1600);
    } catch {
      const range = document.createRange();
      range.selectNodeContents(document.getElementById(button.dataset.copy));
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      document.getElementById("copy-status").textContent =
        "Clipboard unavailable. Text selected; use your keyboard copy command.";
      button.textContent = "Text selected";
      setTimeout(() => (button.textContent = "Copy"), 2200);
    }
  }),
);

const rpidForm = document.getElementById("rpid-form");
if (rpidForm) {
  const rpidInput = document.getElementById("rpid-value"),
    rpidBox = document.getElementById("rpid-generated-box"),
    rpidStatus = document.getElementById("rpid-status");
  rpidInput.addEventListener("input", () => {
    rpidBox.hidden = true;
    document.getElementById("rpid-generated").textContent = "";
    rpidStatus.textContent = "";
  });
  rpidForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const id = rpidInput.value;
    if (!/^[A-Z]{6}[0-9]{4}$/.test(id) || id === "ABCDEF1234") {
      rpidBox.hidden = true;
      rpidStatus.textContent =
        "Enter your actual project RPID; the example ID is not accepted.";
      return;
    }
    document.getElementById("rpid-generated").textContent =
      `# Option A: literal directive near the top of job.pbs\n#PBS -P ${id}\n\n# Option B: on Aqua, supply accounting at submission\nexport AQUA_RPID=${id}\nqsub -P "$AQUA_RPID" job.pbs`;
    rpidBox.hidden = false;
    rpidStatus.textContent =
      "Format accepted. Confirm project authorization before using these commands.";
  });
}

const walltimeForm = document.getElementById("walltime-form");
if (walltimeForm) {
  walltimeForm.addEventListener("input", () => {
    document.getElementById("walltime-result").textContent =
      "Inputs changed. Calculate again to update the estimate.";
  });
  walltimeForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const values = ["startup", "records", "rate", "finalize", "margin", "limit"].map(
      (id) => Number(document.getElementById(id).value),
    );
    const [startup, records, rate, finalize, margin, limit] = values;
    const result = document.getElementById("walltime-result");
    if (
      values.some((n) => !Number.isFinite(n)) ||
      startup < 0 ||
      records < 1 ||
      !Number.isInteger(records) ||
      rate <= 0 ||
      finalize < 0 ||
      margin < 0 ||
      limit <= 0
    ) {
      result.textContent =
        "Enter valid nonnegative times, a positive whole record count, and a positive limit.";
      return;
    }
    const base = startup * 60 + records * rate + finalize * 60,
      seconds = Math.ceil(base * (1 + margin / 100));
    if (!Number.isSafeInteger(seconds)) {
      result.textContent = "Estimate is too large. Check the units and values.";
      return;
    }
    const time = [
      Math.floor(seconds / 3600),
      Math.floor((seconds % 3600) / 60),
      seconds % 60,
    ]
      .map((n) => String(n).padStart(2, "0"))
      .join(":");
    result.textContent =
      `Estimated base: ${(base / 60).toFixed(1)} minutes. With ${margin}% headroom: ${time}. ` +
      (seconds > limit * 3600
        ? "Exceeds the supplied limit. Do not submit with that limit; choose a verified eligible route or validated checkpoint/chunk strategy."
        : "Fits the supplied limit; verify it against current site and user caps.") +
      " Queue wait is unknown.";
  });
}

// Keep all reference text visible in printed copies, including collapsed answers.
let printState = [];
window.addEventListener("beforeprint", () => {
  printState = Array.from(document.querySelectorAll("details"), (d) => [d, d.open]);
  printState.forEach(([d]) => (d.open = true));
});
window.addEventListener("afterprint", () =>
  printState.forEach(([d, open]) => (d.open = open)),
);
