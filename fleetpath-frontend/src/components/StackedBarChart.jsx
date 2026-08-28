import React, { useState } from "react";
import { COLORS, PATHWAY_LABELS, formatMoney } from "../styles";

export default function StackedBarChart({ data }) {
  const [hoveredItem, setHoveredItem] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div style={{ padding: 16, color: COLORS.slateMuted, fontSize: 13, fontStyle: "italic" }}>
        No TCO composition data available.
      </div>
    );
  }

  const currency = data[0]?.currency || "USD";

  const segments = [
    { key: "capex_vehicle_amortized", label: "Vehicle CapEx (Amortized)", color: COLORS.navy },
    { key: "capex_infra_amortized", label: "Infra CapEx (Amortized)", color: "#3B5A8A" },
    { key: "opex_fuel", label: "Annual Fuel/Energy OpEx", color: COLORS.emeraldDark },
    { key: "opex_maintenance", label: "Annual Maintenance OpEx", color: "#0D9488" },
  ];

  const rowData = data.map((d) => {
    const grossTotal = segments.reduce((sum, seg) => sum + (Number(d[seg.key]) || 0), 0);
    return {
      ...d,
      grossTotal,
      netTco: Number(d.tco_total) || grossTotal,
      incentives: Number(d.incentives_applied) || 0,
    };
  });

  const maxVal = Math.max(...rowData.map((d) => d.grossTotal), 1);

  return (
    <div style={{ marginTop: 12, marginBottom: 20 }}>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          marginBottom: 16,
          padding: "8px 12px",
          background: COLORS.bgLight,
          borderRadius: 4,
          border: `1px solid ${COLORS.grayBorder}`,
        }}
      >
        {segments.map((seg) => (
          <div key={seg.key} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: 2,
                backgroundColor: seg.color,
                display: "inline-block",
              }}
            />
            <span style={{ color: COLORS.slate, fontWeight: 500 }}>{seg.label}</span>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        {rowData.map((d) => {
          const isHovered = hoveredItem === d.fuel_type;
          return (
            <div
              key={d.fuel_type}
              onMouseEnter={() => setHoveredItem(d.fuel_type)}
              onMouseLeave={() => setHoveredItem(null)}
              style={{
                padding: "8px 12px",
                borderRadius: 4,
                background: isHovered ? COLORS.bgLight : "transparent",
                border: `1px solid ${isHovered ? COLORS.grayBorder : "transparent"}`,
                transition: "background 0.15s ease",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "baseline",
                  marginBottom: 6,
                }}
              >
                <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.navyDark }}>
                  {PATHWAY_LABELS[d.fuel_type] || d.fuel_type}
                </span>
                <span
                  style={{
                    fontSize: 13,
                    fontWeight: 700,
                    color: COLORS.navy,
                    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                  }}
                >
                  {formatMoney(d.netTco, d.currency || currency)}
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  height: 24,
                  width: "100%",
                  backgroundColor: "#EEF2F6",
                  borderRadius: 4,
                  overflow: "hidden",
                }}
              >
                {segments.map((seg) => {
                  const val = Number(d[seg.key]) || 0;
                  const pct = (val / maxVal) * 100;
                  if (pct <= 0) return null;
                  return (
                    <div
                      key={seg.key}
                      title={`${seg.label}: ${formatMoney(val, d.currency || currency)}`}
                      style={{
                        width: `${pct}%`,
                        backgroundColor: seg.color,
                        height: "100%",
                        position: "relative",
                      }}
                    />
                  );
                })}
              </div>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 12,
                  marginTop: 6,
                  fontSize: 11,
                  color: COLORS.slateMuted,
                }}
              >
                {segments.map((seg) => {
                  const val = Number(d[seg.key]) || 0;
                  return (
                    <span key={seg.key}>
                      <strong style={{ color: COLORS.slate }}>{seg.label.split(" ")[0]}:</strong>{" "}
                      {formatMoney(val, d.currency || currency)}
                    </span>
                  );
                })}
                {d.incentives > 0 && (
                  <span style={{ color: COLORS.emeraldDark, fontWeight: 600 }}>
                    Incentives Offset: -{formatMoney(d.incentives, d.currency || currency)}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
