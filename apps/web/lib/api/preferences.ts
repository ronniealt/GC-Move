import { apiCall } from "./client";
import type { PreferenceResponse, PreferenceUpdate } from "../types";

export function listPreferences(token: string): Promise<PreferenceResponse[]> {
  return apiCall("/api/preferences", { method: "GET", token });
}

export function updatePreference(
  id: string,
  body: PreferenceUpdate,
  token: string
): Promise<PreferenceResponse> {
  return apiCall(`/api/preferences/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
    token,
  });
}

export function retirePreference(id: string, token: string): Promise<void> {
  return apiCall(`/api/preferences/${id}`, { method: "DELETE", token });
}
