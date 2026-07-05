import { apiCall } from "./client";
import type {
  FamilyResponse,
  FamilyMemberResponse,
  FamilyCreateBody,
  FamilyMemberCreate,
  FamilyUpdate,
  FamilyNonNegotiableResponse,
  FamilySuburbsResponse,
  NotificationSettingsResponse,
  NotificationSettingsUpdate,
} from "../types";

export function createFamily(
  body: FamilyCreateBody,
  token: string
): Promise<FamilyResponse> {
  return apiCall("/api/families", {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function getMyFamily(token: string): Promise<FamilyResponse> {
  return apiCall("/api/families/me", { method: "GET", token });
}

export function updateFamily(
  id: string,
  body: FamilyUpdate,
  token: string
): Promise<FamilyResponse> {
  return apiCall(`/api/families/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
    token,
  });
}

export function addFamilyMember(
  familyId: string,
  body: FamilyMemberCreate,
  token: string
): Promise<FamilyMemberResponse> {
  return apiCall(`/api/families/${familyId}/members`, {
    method: "POST",
    body: JSON.stringify(body),
    token,
  });
}

export function getFamilyMembers(
  familyId: string,
  token: string
): Promise<FamilyMemberResponse[]> {
  return apiCall(`/api/families/${familyId}/members`, {
    method: "GET",
    token,
  });
}

export function setNonNegotiables(
  familyId: string,
  labels: string[],
  token: string,
  propertyType?: string
): Promise<{ message: string }> {
  return apiCall(`/api/families/${familyId}/non-negotiables`, {
    method: "PUT",
    body: JSON.stringify({ labels, property_type: propertyType }),
    token,
  });
}

export function getNonNegotiables(
  familyId: string,
  token: string
): Promise<FamilyNonNegotiableResponse[]> {
  return apiCall(`/api/families/${familyId}/non-negotiables`, {
    method: "GET",
    token,
  });
}

export function setTargetSuburbs(
  familyId: string,
  suburbIds: string[],
  token: string
): Promise<{ message: string }> {
  return apiCall(`/api/families/${familyId}/suburbs`, {
    method: "PUT",
    body: JSON.stringify({ suburb_ids: suburbIds }),
    token,
  });
}

export function getTargetSuburbs(
  familyId: string,
  token: string
): Promise<FamilySuburbsResponse> {
  return apiCall(`/api/families/${familyId}/suburbs`, {
    method: "GET",
    token,
  });
}

export function getNotificationSettings(
  familyId: string,
  token: string
): Promise<NotificationSettingsResponse> {
  return apiCall(`/api/families/${familyId}/notification-settings`, {
    method: "GET",
    token,
  });
}

export function updateNotificationSettings(
  familyId: string,
  body: NotificationSettingsUpdate,
  token: string
): Promise<NotificationSettingsResponse> {
  return apiCall(`/api/families/${familyId}/notification-settings`, {
    method: "PATCH",
    body: JSON.stringify(body),
    token,
  });
}
