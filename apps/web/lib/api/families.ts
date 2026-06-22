import { apiCall } from "./client";
import type {
  FamilyResponse,
  FamilyMemberResponse,
  FamilyCreateBody,
  FamilyMemberCreate,
  FamilyUpdate,
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
