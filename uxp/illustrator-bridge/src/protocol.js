export const METHODS = Object.freeze([
  "illustrator.get_state",
  "illustrator.document_info",
  "illustrator.select_object",
  "illustrator.set_fill",
  "illustrator.move_object",
  "illustrator.create_path",
  "illustrator.zoom_to_selection",
]);

export const WRITE_METHODS = new Set([
  "illustrator.select_object",
  "illustrator.set_fill",
  "illustrator.move_object",
  "illustrator.create_path",
]);

export function validateRequest(message) {
  if (!message || message.jsonrpc !== "2.0" || !("id" in message)) return "invalid_jsonrpc_request";
  if (!METHODS.includes(message.method)) return "method_not_allowed";
  if (!message.params || typeof message.params !== "object" || Array.isArray(message.params)) return "params_must_be_object";
  if (WRITE_METHODS.has(message.method) && message.params.confirm_write !== true) return "confirm_write=true_required";
  if (message.params.object_id !== undefined && !/^item:\d+$/.test(String(message.params.object_id))) return "object_id_must_be_session_local";
  return null;
}

export function rpcResult(id, result) { return {jsonrpc: "2.0", id, result}; }
export function rpcError(id, code, message) { return {jsonrpc: "2.0", id: id ?? null, error: {code, message}}; }
