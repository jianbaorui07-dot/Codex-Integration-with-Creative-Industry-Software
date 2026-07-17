import { invoke as tauriInvoke } from "@tauri-apps/api/core";

import type {
  RuntimeStatus,
  TransportRequest,
  TransportResponse,
  VersionInfo,
} from "../types/api";
import { TransportError, type StarBridgeTransport } from "./transport";

export type InvokeLike = <T>(command: string, args?: Record<string, unknown>) => Promise<T>;

export class DesktopTransport implements StarBridgeTransport {
  readonly kind = "desktop" as const;

  constructor(private readonly invoke: InvokeLike = tauriInvoke) {}

  private async call<T>(command: string, args?: Record<string, unknown>): Promise<T> {
    try {
      return await this.invoke<T>(command, args);
    } catch (error) {
      throw new TransportError(
        "desktop_invoke_failed",
        "StarBridge Desktop 暂时无法完成该操作。",
        error instanceof Error ? error.message : String(error),
      );
    }
  }

  request<T>(request: TransportRequest): Promise<TransportResponse<T>> {
    return this.call<TransportResponse<T>>("backend_request", { request });
  }

  getRuntimeStatus(): Promise<RuntimeStatus> {
    return this.call<RuntimeStatus>("backend_status");
  }

  restartBackend(): Promise<RuntimeStatus> {
    return this.call<RuntimeStatus>("restart_backend");
  }

  openLogsDirectory(): Promise<string> {
    return this.call<string>("open_logs_directory");
  }

  getVersion(): Promise<VersionInfo> {
    return this.call<VersionInfo>("version_info");
  }
}
