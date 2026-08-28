export const COLORS = {
  navy: "#1B2A4A",
  navyDark: "#0F172A",
  slate: "#334155",
  slateMuted: "#475569",
  slateLight: "#64748B",
  emerald: "#1F9D6E",
  emeraldDark: "#15803D",
  emeraldBg: "#F0FDF4",
  emeraldBorder: "#86EFAC",
  grayBorder: "#E2E8F0",
  grayBorderDark: "#CBD5E1",
  bgLight: "#F8FAFC",
  bgCard: "#FFFFFF",
  danger: "#B91C1C",
  dangerBg: "#FEF2F2",
  dangerBorder: "#FCA5A5",
  amber: "#B45309",
  amberBg: "#FFFBEB",
  blue: "#0284C7",
  purple: "#7C3AED",
  rust: "#C2410C",
};

export const PATHWAY_LABELS = {
  diesel: "Diesel",
  bev: "Battery-Electric",
  hydrogen: "Hydrogen Fuel Cell",
  cng: "CNG",
  biodiesel: "Biodiesel (B20)",
};

// DISCLOSED CHANGE: trimmed to states with real crosswalk/grid-factor data.
// NY/MI/OH/PA/IL/CO previously listed but caused UnknownRegionError on submit.
// Re-add only after real eGRID sourcing + crosswalk/grid_factors entries exist.
export const US_STATES = ["IN", "CA", "TX", "WA"];
export const CA_PROVINCES = ["ON", "QC", "BC", "AB", "NB"];

export const VEHICLE_TYPES = [
  { value: "school_bus_typeC", label: "School Bus (Type C)" },
  { value: "transit_short_haul", label: "Transit Bus (Short-Haul)" },
  { value: "utility_medium_duty", label: "Utility Truck (Class 4-6)" },
];

export function formatMoney(value, currency = "USD") {
  if (value === null || value === undefined || isNaN(Number(value))) return "—";
  return `$${Math.round(Number(value)).toLocaleString("en-US")} ${currency}`;
}

export function formatTons(value) {
  if (value === null || value === undefined || isNaN(Number(value))) return "—";
  return `${Number(value).toLocaleString("en-US", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} t`;
}

export function formatYears(value) {
  if (value === null || value === undefined) return "Not recovered in lifecycle";
  return `${Number(value).toFixed(1)} yrs`;
}

export function formatPct(value) {
  if (value === null || value === undefined || isNaN(Number(value))) return "—";
  return `${Number(value).toFixed(1)}%`;
}

export const cardStyle = {
  background: COLORS.bgCard,
  border: `1px solid ${COLORS.grayBorder}`,
  borderRadius: 6,
  padding: 24,
  boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.05)",
};

export const errorStyle = {
  color: COLORS.danger,
  fontSize: 12,
  marginTop: 4,
  marginBottom: 0,
};

export const cellStyle = {
  borderBottom: `1px solid ${COLORS.grayBorder}`,
  padding: "10px 12px",
  textAlign: "left",
  fontSize: 13,
  color: COLORS.navyDark,
};

export const cellHeaderStyle = {
  borderBottom: `2px solid ${COLORS.grayBorder}`,
  padding: "10px 12px",
  textAlign: "left",
  fontSize: 11,
  fontWeight: 600,
  letterSpacing: "0.05em",
  textTransform: "uppercase",
  color: COLORS.slateMuted,
  background: COLORS.bgLight,
};

export const labelStyle = {
  display: "block",
  fontSize: 13,
  fontWeight: 500,
  color: COLORS.slate,
  marginTop: 14,
  marginBottom: 4,
};

export const inputStyle = {
  width: "100%",
  padding: "9px 12px",
  border: `1px solid ${COLORS.grayBorderDark}`,
  borderRadius: 4,
  fontSize: 14,
  color: COLORS.navyDark,
  backgroundColor: "#FFFFFF",
  boxSizing: "border-box",
  fontFamily: "inherit",
};

export const secondaryButtonStyle = {
  background: "#FFFFFF",
  border: `1px solid ${COLORS.grayBorderDark}`,
  color: COLORS.slate,
  padding: "8px 16px",
  borderRadius: 4,
  cursor: "pointer",
  fontSize: 13,
  fontWeight: 500,
  transition: "all 0.15s ease",
};

export function primaryButtonStyle(disabled) {
  return {
    background: disabled ? "#94A3B8" : COLORS.navy,
    border: "none",
    color: "#FFFFFF",
    padding: "8px 20px",
    borderRadius: 4,
    cursor: disabled ? "not-allowed" : "pointer",
    fontSize: 13,
    fontWeight: 600,
    letterSpacing: "0.01em",
    transition: "all 0.15s ease",
  };
}
