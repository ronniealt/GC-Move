import { apiCall } from "./client";
import type { EvaluationResponse } from "../types";

export function getEvaluation(
  propertyId: string,
  token: string
): Promise<EvaluationResponse> {
  return apiCall(`/api/evaluations/${propertyId}`, { method: "GET", token });
}
