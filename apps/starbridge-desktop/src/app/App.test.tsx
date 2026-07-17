import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import type { StarBridgeClient } from "../services/client";
import { UserFacingError } from "../services/client";
import type { RuntimeStatus } from "../types/api";
import { App } from "./App";

function makeClient(status: RuntimeStatus | Promise<RuntimeStatus>): StarBridgeClient {
  return {
    getRuntimeStatus: vi.fn().mockImplementation(() => Promise.resolve(status)),
    getHealth: vi.fn().mockResolvedValue({ ok: true }),
    getBootstrap: vi.fn().mockResolvedValue({ ok: true }),
    restartBackend: vi.fn().mockResolvedValue({
      state: "connected",
      message: "本地服务已恢复。",
      recoveryAttempts: 1,
    }),
    openLogsDirectory: vi.fn().mockResolvedValue("<LOCAL_APP_DATA>/StarBridge/logs"),
    getVersion: vi.fn().mockResolvedValue({ desktop: "0.1.0" }),
  };
}

describe("desktop runtime status", () => {
  it("shows the starting state before the runtime responds", () => {
    const pending = new Promise<RuntimeStatus>(() => undefined);
    render(<App client={makeClient(pending)} />);

    expect(screen.getByText("正在启动 StarBridge")).toBeInTheDocument();
  });

  it("shows a connected state in ordinary language", async () => {
    render(
      <App
        client={makeClient({
          state: "connected",
          message: "安全本地服务已经就绪。",
          recoveryAttempts: 0,
          port: 49152,
        })}
      />,
    );

    expect(await screen.findByText("本地服务已连接")).toBeInTheDocument();
    expect(screen.getByText("安全本地服务已经就绪。")).toBeInTheDocument();
    expect(screen.queryByText(/49152/)).not.toBeInTheDocument();
  });

  it("shows offline recovery guidance and technical details", async () => {
    render(
      <App
        client={makeClient({
          state: "offline",
          message: "没有检测到本地服务，请尝试重新启动。",
          recoveryAttempts: 1,
          technicalDetails: "backend process not found",
        })}
      />,
    );

    expect(await screen.findByText("本地服务尚未连接")).toBeInTheDocument();
    expect(screen.getByText("重新启动本地服务")).toBeInTheDocument();
    expect(screen.getByText("查看技术详情")).toBeInTheDocument();
    expect(screen.getByText("backend process not found")).toBeInTheDocument();
  });

  it("turns a 401 or 403 style error into a user-facing failure", async () => {
    const client = makeClient({
      state: "connected",
      message: "connected",
      recoveryAttempts: 0,
    });
    client.getRuntimeStatus = vi.fn().mockRejectedValue(
      new UserFacingError(
        "authentication_failed",
        "桌面会话已失效，请重新启动本地服务。",
        "HTTP 403; authentication_failed",
        [],
        403,
      ),
    );
    render(<App client={client} />);

    expect(await screen.findByText("本地服务启动失败")).toBeInTheDocument();
    expect(screen.getByText("桌面会话已失效，请重新启动本地服务。")).toBeInTheDocument();
    expect(screen.getByText("HTTP 403; authentication_failed")).toBeInTheDocument();
  });

  it("offers a manual restart and reports recovery", async () => {
    const client = makeClient({
      state: "failed",
      message: "启动失败。",
      recoveryAttempts: 1,
    });
    render(<App client={client} />);
    await screen.findByText("本地服务启动失败");

    fireEvent.click(screen.getByRole("button", { name: "重新启动本地服务" }));

    await waitFor(() => expect(client.restartBackend).toHaveBeenCalledOnce());
    expect(await screen.findByText("本地服务已恢复。")).toBeInTheDocument();
  });
});
