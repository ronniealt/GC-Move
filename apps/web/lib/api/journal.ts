import { apiCall } from "./client";
import type { JournalEntryCreate, JournalEntryResponse } from "../types";

export function listJournalEntries(token: string): Promise<JournalEntryResponse[]> {
  return apiCall("/api/journal", { method: "GET", token });
}

export function createJournalEntry(
  body: JournalEntryCreate,
  token: string
): Promise<JournalEntryResponse> {
  return apiCall("/api/journal", {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function getJournalEntry(id: string, token: string): Promise<JournalEntryResponse> {
  return apiCall(`/api/journal/${id}`, { method: "GET", token });
}

export function deleteJournalEntry(id: string, token: string): Promise<void> {
  return apiCall(`/api/journal/${id}`, { method: "DELETE", token });
}
