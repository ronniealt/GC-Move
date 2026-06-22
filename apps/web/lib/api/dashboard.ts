import { apiCall } from "./client";
import type { DashboardResponse } from "../types";

export function getDashboard(token: string): Promise<DashboardResponse> {
  return apiCall("/api/dashboard", { method: "GET", token });
}
