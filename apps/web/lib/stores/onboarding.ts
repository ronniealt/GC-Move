import { create } from "zustand";

interface FamilyMemberDraft {
  name: string;
  role: string;
  age: string;
}

interface OnboardingState {
  step: number;
  familyName: string;
  members: FamilyMemberDraft[];
  budgetMin: string;
  budgetMax: string;
  moveTimeline: string;
  nonNegotiables: string[];
  targetSuburbIds: string[];
  setStep: (step: number) => void;
  setFamilyName: (name: string) => void;
  setMembers: (members: FamilyMemberDraft[]) => void;
  setBudget: (min: string, max: string) => void;
  setMoveTimeline: (timeline: string) => void;
  setNonNegotiables: (items: string[]) => void;
  setTargetSuburbIds: (ids: string[]) => void;
  reset: () => void;
}

const initialState = {
  step: 1,
  familyName: "",
  members: [],
  budgetMin: "",
  budgetMax: "",
  moveTimeline: "",
  nonNegotiables: [],
  targetSuburbIds: [],
};

export const useOnboardingStore = create<OnboardingState>((set) => ({
  ...initialState,
  setStep: (step) => set({ step }),
  setFamilyName: (familyName) => set({ familyName }),
  setMembers: (members) => set({ members }),
  setBudget: (budgetMin, budgetMax) => set({ budgetMin, budgetMax }),
  setMoveTimeline: (moveTimeline) => set({ moveTimeline }),
  setNonNegotiables: (nonNegotiables) => set({ nonNegotiables }),
  setTargetSuburbIds: (targetSuburbIds) => set({ targetSuburbIds }),
  reset: () => set(initialState),
}));
