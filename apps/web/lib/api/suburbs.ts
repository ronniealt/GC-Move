import { apiCall } from "./client";
import type { SuburbDetailResponse, SuburbListItem } from "../types";

export function listSuburbs(token: string): Promise<SuburbListItem[]> {
  return apiCall("/api/suburbs", { method: "GET", token });
}

export function getSuburb(slug: string, token: string): Promise<SuburbDetailResponse> {
  return apiCall(`/api/suburbs/${slug}`, { method: "GET", token });
}
