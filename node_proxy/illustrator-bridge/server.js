import http from "node:http";
import { URL } from "node:url";
import { WebSocketServer } from "ws";

const PORT = Number(process.env.STARBRIDGE_ILLUSTRATOR_PROXY_PORT || 8972);
const MAX_FRAME_BYTES = 4 * 1024 * 1024;
const WRITE_METHODS = new Set(["illustrator.select_object", "illustrator.set_fill", "illustrator.move_object", "illustrator.create_path"]);
const METHODS = new Set(["illustrator.get_state", "illustrator.document_info", "illustrator.zoom_to_selection", ...WRITE_METHODS]);
let adapter = null;
let latestState = null;
let latestFrame = null;
const pending = new Map();
const status = { adapter_connected: false, capture_connected: false, last_state_at: null, last_frame_at: null, pending_jobs: 0, last_error: null };

function json(res, code, value) { res.writeHead(code, {"Content-Type": "application/json; charset=utf-8"}); res.end(JSON.stringify(value)); }
function error(id, code, message) { return {jsonrpc: "2.0", id: id ?? null, error: {code, message}}; }
function safeString(value) { return typeof value === "string" && !/[\\/]:?|file:|users\\|home\\/i.test(value); }
function validate(message) {
  if (!message || message.jsonrpc !== "2.0" || !("id" in message) || !METHODS.has(message.method)) return error(message?.id, -32600, "invalid_or_unlisted_method");
  if (!message.params || typeof message.params !== "object" || Array.isArray(message.params)) return error(message.id, -32602, "params_must_be_object");
  if (WRITE_METHODS.has(message.method) && message.params.confirm_write !== true) return error(message.id, -32010, "confirm_write=true_required");
  if (message.params.object_id !== undefined && !safeString(message.params.object_id)) return error(message.id, -32602, "object_id_must_be_session_local");
  return null;
}
async function body(req, limit = MAX_FRAME_BYTES) { const chunks=[]; let size=0; for await (const chunk of req) { size += chunk.length; if (size > limit) throw new Error("payload_too_large"); chunks.push(chunk); } return Buffer.concat(chunks); }
function health() { return {ok: true, node_proxy_running: true, websocket_enabled: true, ...status, has_state: Boolean(latestState), has_frame: Boolean(latestFrame)}; }
function forward(message) { return new Promise((resolve) => { if (!adapter || adapter.readyState !== 1) return resolve(error(message.id, -32001, "illustrator_adapter_not_connected")); pending.set(message.id, resolve); status.pending_jobs=pending.size; adapter.send(JSON.stringify(message)); setTimeout(()=>{ if(pending.delete(message.id)){ status.pending_jobs=pending.size; resolve(error(message.id,-32002,"adapter_timeout"));}},8000); }); }

const server = http.createServer(async (req,res) => {
  const url = new URL(req.url || "/", `http://127.0.0.1:${PORT}`);
  try {
    if (req.method === "GET" && url.pathname === "/health") return json(res,200,health());
    if (req.method === "GET" && url.pathname === "/preview") {
      res.writeHead(200,{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store"});
      return res.end(`<!doctype html><meta charset="utf-8"><title>StarBridge Illustrator Preview</title><style>html,body{margin:0;background:#111;color:#ddd;font:14px system-ui;height:100%}body{display:grid;grid-template-rows:auto 1fr}header{padding:8px 12px;background:#202020}img{width:100%;height:100%;object-fit:contain;min-height:0}</style><header>Illustrator 窗口实时预览 · <span id="status">连接中</span></header><img id="frame" alt="Illustrator window preview"><script>const image=document.querySelector('#frame'),status=document.querySelector('#status');let last='';async function tick(){try{const meta=await fetch('/frame/meta',{cache:'no-store'}).then(r=>r.json());if(meta.ok&&meta.frame.at!==last){last=meta.frame.at;image.src='/frame/latest?t='+encodeURIComponent(last);status.textContent=meta.frame.width+'×'+meta.frame.height+' · '+new Date(last).toLocaleTimeString();}}catch(e){status.textContent='等待代理';}}setInterval(tick,250);tick();</script>`);
    }
    if (req.method === "GET" && url.pathname === "/state") return json(res,200,{ok:Boolean(latestState), state:latestState});
    if (req.method === "GET" && url.pathname === "/frame/meta") return json(res,200,{ok:Boolean(latestFrame), frame:latestFrame ? {...latestFrame, data:undefined} : null});
    if (req.method === "GET" && url.pathname === "/frame/latest") { if(!latestFrame){return json(res,404,{ok:false,message:"frame_unavailable"});} res.writeHead(200,{"Content-Type":latestFrame.content_type,"Cache-Control":"no-store","X-StarBridge-Capture":"illustrator-window"}); return res.end(latestFrame.data); }
    if (req.method === "POST" && url.pathname === "/capture/frame") {
      if (req.headers["x-starbridge-capture-target"] !== "illustrator-window") return json(res,400,{ok:false,message:"desktop_capture_rejected"});
      const data=await body(req); const contentType=String(req.headers["content-type"]||""); if(!["image/jpeg","image/png"].includes(contentType)) return json(res,415,{ok:false,message:"frame_must_be_jpeg_or_png"});
      latestFrame={data,content_type:contentType,bytes:data.length,width:Number(req.headers["x-frame-width"]||0),height:Number(req.headers["x-frame-height"]||0),at:new Date().toISOString()}; status.capture_connected=true; status.last_frame_at=latestFrame.at; return json(res,202,{ok:true,bytes:data.length});
    }
    if (req.method === "POST" && url.pathname === "/rpc") { const message=JSON.parse((await body(req,256*1024)).toString("utf8")); const invalid=validate(message); if(invalid)return json(res,200,invalid); return json(res,200,await forward(message)); }
    return json(res,404,{ok:false,message:"not_found"});
  } catch (e) { status.last_error=String(e?.message||e); return json(res,400,{ok:false,message:status.last_error}); }
});

const wss = new WebSocketServer({noServer:true});
server.on("upgrade",(req,socket,head)=>{ if(req.url !== "/illustrator"){socket.destroy();return;} wss.handleUpgrade(req,socket,head,ws=>wss.emit("connection",ws)); });
wss.on("connection",ws=>{ adapter=ws; status.adapter_connected=true; ws.on("message",raw=>{ let msg; try{msg=JSON.parse(String(raw));}catch{return;} if(msg.type === "state"){ latestState=msg; status.last_state_at=new Date().toISOString(); return; } const done=pending.get(msg.id); if(done){pending.delete(msg.id);status.pending_jobs=pending.size;done(msg);} }); ws.on("close",()=>{if(adapter===ws)adapter=null;status.adapter_connected=false;}); });
server.listen(PORT,"127.0.0.1");
