import { apiCall } from "./client";
import type { InspectionCreate, InspectionResponse, InspectionUpdate } from "../types";

export function listInspections(token: string): Promise<InspectionResponse[]> {
  return apiCall("/api/inspections", { token });
}

export function createInspection(
  body: InspectionCreate,
  token: string
): Promise<InspectionResponse> {
  return apiCall("/api/inspections", {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function updateInspection(
  id: string,
  body: InspectionUpdate,
  token: string
): Promise<InspectionResponse> {
  return apiCall(`/api/inspections/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
    token,
  });
}

export function deleteInspection(id: string, token: string): Promise<void> {
  return apiCall(`/api/inspections/${id}`, { method: "DELETE", token });
}
