import fs from "node:fs";

import Ajv from "ajv";

const readJson = (relativePath) =>
  JSON.parse(fs.readFileSync(new URL(relativePath, import.meta.url), "utf8"));

const mergePatch = (base, patch) => {
  if (patch === null || Array.isArray(patch) || typeof patch !== "object") {
    return patch;
  }

  const merged =
    base !== null && !Array.isArray(base) && typeof base === "object"
      ? { ...base }
      : {};
  for (const [key, value] of Object.entries(patch)) {
    if (value === null) {
      delete merged[key];
    } else {
      merged[key] = mergePatch(merged[key], value);
    }
  }
  return merged;
};

const schema = readJson("../node_modules/@tauri-apps/cli/config.schema.json");
const base = readJson("../src-tauri/tauri.conf.json");
const windows = mergePatch(
  base,
  readJson("../src-tauri/tauri.windows.conf.json"),
);
const validate = new Ajv({
  allErrors: true,
  strict: false,
  unicodeRegExp: false,
  validateFormats: false,
}).compile(schema);

for (const [name, config] of [
  ["tauri.conf.json", base],
  ["tauri.conf.json + tauri.windows.conf.json", windows],
]) {
  if (!validate(config)) {
    const details = validate.errors
      .map(({ instancePath, message }) => `${instancePath || "/"} ${message}`)
      .join("; ");
    throw new Error(
      `${name} does not match the installed Tauri v2 schema: ${details}`,
    );
  }
}

console.log("Tauri v2 schema check passed for base and Windows configuration.");
