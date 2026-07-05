// Must match the label -> criterion mapping in apps/api/app/routers/families.py's
// NON_NEGOTIABLE_LABEL_MAP.
export const NON_NEGOTIABLE_OPTIONS = [
  "4+ bedrooms",
  "Pool",
  "Double garage",
  "Somerset College catchment",
  "Beach < 10 min",
  "Home office",
];

export const MAX_TARGET_SUBURBS = 7;

export const PROPERTY_TYPE_OPTIONS = [
  { value: "house", label: "House" },
  { value: "townhouse", label: "Townhouse" },
  { value: "unit", label: "Unit" },
  { value: "acreage", label: "Acreage" },
  { value: "any", label: "Any" },
];
