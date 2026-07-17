export type RuntimeState =
  | "starting"
  | "connected"
  | "offline"
  | "recovering"
  | "failed";

export interface RuntimeStatus {
  state: RuntimeState;
  message: string;
  backendPid?: number;
  port?: number;
  recoveryAttempts: number;
  technicalDetails?: string;
}

export interface VersionInfo {
  desktop: string;
  backend?: string;
}

export interface ApiErrorShape {
  code?: string;
  message?: string;
  next_steps?: string[];
}

export interface ApiEnvelope<T> {
  ok: boolean;
  data?: T;
  error?: ApiErrorShape | string;
  [key: string]: unknown;
}

export interface TransportResponse<T> {
  status: number;
  body: T;
}

export interface TransportRequest {
  method: "GET" | "POST";
  path: string;
  body?: Record<string, unknown>;
}
