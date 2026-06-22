import { apiCall } from "./client";
import type {
  AdvisorMessageRequest,
  AdvisorMessageResponse,
  AdvisorHistoryResponse,
} from "../types";

export function sendMessage(
  body: AdvisorMessageRequest,
  token: string
): Promise<AdvisorMessageResponse> {
  return apiCall("/api/advisor/chat", {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function getHistory(token: string): Promise<AdvisorHistoryResponse> {
  return apiCall("/api/advisor/history", { method: "GET", token });
}
