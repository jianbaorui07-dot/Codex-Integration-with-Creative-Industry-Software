import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  StarBridgeApiClient,
  UserFacingError,
  type StarBridgeClient,
} from "../services/client";
import type { RuntimeState, RuntimeStatus, VersionInfo } from "../types/api";

const STATE_COPY: Record<
  RuntimeState,
  { eyebrow: string; title: string; description: string }
> = {
  starting: {
    eyebrow: "STARTING",
    title: "正在启动 StarBridge",
    description: "正在准备本地安全服务，通常只需要几秒钟。",
  },
  connected: {
    eyebrow: "CONNECTED",
    title: "本地服务已连接",
    description: "你可以继续进行安全检查、计划生成和结果验证。",
  },
  offline: {
    eyebrow: "OFFLINE",
    title: "本地服务尚未连接",
    description: "请重新启动本地服务；如果仍未恢复，再查看诊断信息。",
  },
  recovering: {
    eyebrow: "RECOVERING",
    title: "正在恢复本地服务",
    description: "StarBridge 只会自动恢复一次，不会无限重启。",
  },
  failed: {
    eyebrow: "NEEDS ATTENTION",
    title: "本地服务启动失败",
    description: "你的文件没有被修改。请查看诊断信息或手动重试。",
  },
};

const INITIAL_STATUS: RuntimeStatus = {
  state: "starting",
  message: "正在等待本地服务报告就绪状态。",
  recoveryAttempts: 0,
};

interface AppProps {
  client?: StarBridgeClient;
}

function statusFromError(error: unknown): RuntimeStatus {
  if (error instanceof UserFacingError) {
    return {
      state: error.code === "backend_offline" ? "offline" : "failed",
      message: error.message,
      recoveryAttempts: 0,
      technicalDetails: error.technicalDetails,
    };
  }
  return {
    state: "failed",
    message: "本地服务状态暂时无法确认。",
    recoveryAttempts: 0,
    technicalDetails: error instanceof Error ? error.message : String(error),
  };
}

export function App({ client: providedClient }: AppProps) {
  const client = useMemo(() => providedClient ?? new StarBridgeApiClient(), [providedClient]);
  const [status, setStatus] = useState<RuntimeStatus>(INITIAL_STATUS);
  const [version, setVersion] = useState<VersionInfo | null>(null);
  const [actionMessage, setActionMessage] = useState<string>("");
  const mounted = useRef(true);

  const refreshStatus = useCallback(async () => {
    try {
      const nextStatus = await client.getRuntimeStatus();
      if (mounted.current) {
        setStatus(nextStatus);
      }
    } catch (error) {
      if (mounted.current) {
        setStatus(statusFromError(error));
      }
    }
  }, [client]);

  useEffect(() => {
    mounted.current = true;
    void refreshStatus();
    void client
      .getVersion()
      .then((nextVersion) => mounted.current && setVersion(nextVersion))
      .catch(() => undefined);
    return () => {
      mounted.current = false;
    };
  }, [client, refreshStatus]);

  useEffect(() => {
    if (status.state !== "starting" && status.state !== "recovering") {
      return undefined;
    }
    const timer = window.setTimeout(() => void refreshStatus(), 600);
    return () => window.clearTimeout(timer);
  }, [refreshStatus, status.state]);

  const restart = async () => {
    setActionMessage("");
    setStatus({
      state: "recovering",
      message: "正在重新启动本地服务。",
      recoveryAttempts: status.recoveryAttempts,
    });
    try {
      setStatus(await client.restartBackend());
    } catch (error) {
      setStatus(statusFromError(error));
    }
  };

  const openLogs = async () => {
    setActionMessage("");
    try {
      const openedPath = await client.openLogsDirectory();
      setActionMessage(`已打开日志目录：${openedPath}`);
    } catch (error) {
      const result = statusFromError(error);
      setActionMessage(result.message);
      setStatus((current) => ({
        ...current,
        technicalDetails: result.technicalDetails,
      }));
    }
  };

  const copy = STATE_COPY[status.state];

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand" aria-label="StarBridge Desktop">
          <span className="brand-mark" aria-hidden="true">
            S
          </span>
          <span>
            <strong>StarBridge</strong>
            <small>DESKTOP FOUNDATION</small>
          </span>
        </div>
        <span className="version" aria-label="版本信息">
          {version ? `Desktop ${version.desktop}` : "正在读取版本"}
        </span>
      </header>

      <section className="workspace" aria-labelledby="runtime-title">
        <div className="intro">
          <p className="section-label">本地运行状态</p>
          <h1 id="runtime-title">安全桌面运行基座</h1>
          <p>
            本阶段只负责安全启动、连接和诊断。工作流中心与完整任务界面将在后续阶段逐步加入。
          </p>
        </div>

        <article className={`status-card status-${status.state}`} aria-live="polite">
          <div className="status-indicator" aria-hidden="true" />
          <div className="status-content">
            <span className="status-eyebrow">{copy.eyebrow}</span>
            <h2>{copy.title}</h2>
            <p>{status.message || copy.description}</p>

            <dl className="status-facts">
              <div>
                <dt>本地服务</dt>
                <dd>{status.state === "connected" ? "已连接" : "等待处理"}</dd>
              </div>
              <div>
                <dt>自动恢复</dt>
                <dd>{status.recoveryAttempts}/1 次</dd>
              </div>
              <div>
                <dt>网络范围</dt>
                <dd>仅本机</dd>
              </div>
            </dl>

            <div className="actions">
              <button type="button" className="primary" onClick={() => void restart()}>
                重新启动本地服务
              </button>
              <button type="button" className="secondary" onClick={() => void openLogs()}>
                打开日志目录
              </button>
            </div>
            {actionMessage ? <p className="action-message">{actionMessage}</p> : null}

            {status.technicalDetails ? (
              <details className="technical-details">
                <summary>查看技术详情</summary>
                <pre>{status.technicalDetails}</pre>
              </details>
            ) : null}
          </div>
        </article>

        <aside className="safety-note">
          <div aria-hidden="true">✓</div>
          <div>
            <h2>当前仍处于安全计划与验证阶段</h2>
            <p>
              文件默认留在本机。真实写入仍需明确确认，并继续受 safe roots、dry-run 和路径脱敏规则约束。
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}
