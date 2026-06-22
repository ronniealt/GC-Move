import { apiCall } from "./client";
import type { SchoolListItem } from "../types";

export function listSchools(token: string): Promise<SchoolListItem[]> {
  return apiCall("/api/schools", { method: "GET", token });
}
