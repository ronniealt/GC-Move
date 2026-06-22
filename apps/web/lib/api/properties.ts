import { apiCall } from "./client";
import type {
  PropertyResponse,
  PropertyListResponse,
  PropertyIngestRequest,
  PropertyIngestResponse,
} from "../types";

export function ingestProperty(
  body: PropertyIngestRequest,
  token: string
): Promise<PropertyIngestResponse> {
  return apiCall("/api/properties/ingest", {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function listProperties(token: string): Promise<PropertyListResponse[]> {
  return apiCall("/api/properties", { method: "GET", token });
}

export function getProperty(
  id: string,
  token: string
): Promise<PropertyResponse> {
  return apiCall(`/api/properties/${id}`, { method: "GET", token });
}

export function updateProperty(
  id: string,
  body: { status?: string; is_favourite?: boolean; family_notes?: string },
  token: string
): Promise<PropertyResponse> {
  return apiCall(`/api/properties/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
    token,
  });
}
