import React, { useState } from "react";
import { COLORS, PATHWAY_LABELS, formatMoney } from "../styles";

export default function PaybackLineChart({ vectors, yearsAxis }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!vectors || vectors.length === 0 || !yearsAxis || yearsAxis.length === 0) {
    return (
      <div style={{ padding: 16, color: COLORS.slateMuted, fontSize: 13, fontStyle: "italic" }}>
        No payback trajectory data available.
      </div>
    );
  }

  const currency = vectors[0]?.currency || "USD";

  const width = 680;
  const height = 320;
  const leftPad = 85;
  const rightPad = 25;
  const topPad = 25;
  const bottomPad = 40;
  const chartWidth = width - leftPad - rightPad;
  const chartHeight = height - topPad - bottomPad;

  const allValues = vectors.flatMap((v) => v.cumulative_cost_by_year || []);
  if (allValues.length === 0) {
    return null;
  }

  const maxVal = Math.max(...allValues, 1000);
  const minVal = Math.min(...allValues, 0);
  const valRange = maxVal - minVal || 1;

  const lineColors = {
    diesel: COLORS.navy,
    bev: COLORS.emeraldDark,
    hydrogen: COLORS.blue,
    cng: COLORS.rust,
    biodiesel: COLORS.purple,
  };

  const xFor = (yearIndex) =>
    leftPad + (yearIndex / (yearsAxis.length - 1)) * chartWidth;
  const yFor = (value) =>
    topPad + chartHeight - ((value - minVal) / valRange) * chartHeight;

  // Generate 4-5 Y-axis grid tick levels
  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((ratio) => minVal + ratio * valRange);

  const formatShortMoney = (val) => {
    if (val >= 1_000_000) {
      return `$${(val / 1_000_000).toFixed(1)}M`;
    }
    if (val >= 1_000) {
      return `$${Math.round(val / 1_000)}k`;
    }
    return `$${Math.round(val)}`;
  };

  return (
    <div style={{ marginTop: 12, marginBottom: 20 }}>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          marginBottom: 14,
          padding: "8px 12px",
          background: COLORS.bgLight,
          borderRadius: 4,
          border: `1px solid ${COLORS.grayBorder}`,
        }}
      >
        {vectors.map((v) => {
          const finalCost = v.cumulative_cost_by_year?.[v.cumulative_cost_by_year.length - 1];
          return (
            <div key={v.fuel_type} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12 }}>
              <span
                style={{
                  width: 14,
                  height: 3,
                  backgroundColor: lineColors[v.fuel_type] || COLORS.slate,
                  display: "inline-block",
                }}
              />
              <span style={{ fontWeight: 600, color: COLORS.navyDark }}>
                {PATHWAY_LABELS[v.fuel_type] || v.fuel_type}:
              </span>
              <span style={{ color: COLORS.slateMuted, fontFamily: "ui-monospace, monospace" }}>
                {formatMoney(finalCost, v.currency || currency)}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{ width: "100%", overflowX: "auto" }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: "100%", maxWidth: width, height: "auto", display: "block" }}
        >
          {yTicks.map((tickVal, i) => {
            const y = yFor(tickVal);
            return (
              <g key={i}>
                <line
                  x1={leftPad}
                  y1={y}
                  x2={leftPad + chartWidth}
                  y2={y}
                  stroke="#E2E8F0"
                  strokeDasharray="3 3"
                />
                <text
                  x={leftPad - 10}
                  y={y + 4}
                  fontSize="11"
                  textAnchor="end"
                  fill={COLORS.slateMuted}
                  fontFamily="Inter, sans-serif"
                >
                  {formatShortMoney(tickVal)} {currency}
                </text>
              </g>
            );
          })}

          {yearsAxis.map((year, idx) => {
            // Show first, last, and every 2-3 years to avoid clutter
            const showTick =
              idx === 0 ||
              idx === yearsAxis.length - 1 ||
              idx % Math.ceil(yearsAxis.length / 6) === 0;
            if (!showTick) return null;
            const x = xFor(idx);
            return (
              <g key={year}>
                <line
                  x1={x}
                  y1={topPad + chartHeight}
                  x2={x}
                  y2={topPad + chartHeight + 5}
                  stroke="#94A3B8"
                />
                <text
                  x={x}
                  y={topPad + chartHeight + 18}
                  fontSize="11"
                  textAnchor="middle"
                  fill={COLORS.slate}
                  fontFamily="Inter, sans-serif"
                >
                  Yr {year}
                </text>
              </g>
            );
          })}

          {vectors.map((v) => {
            const points = (v.cumulative_cost_by_year || [])
              .map((val, idx) => `${xFor(idx)},${yFor(val)}`)
              .join(" ");
            const isDiesel = v.fuel_type === "diesel";
            return (
              <g key={v.fuel_type}>
                <polyline
                  points={points}
                  fill="none"
                  stroke={lineColors[v.fuel_type] || COLORS.slate}
                  strokeWidth={isDiesel ? "2.5" : "2"}
                  strokeDasharray={isDiesel ? "4 3" : undefined}
                />
                {(v.cumulative_cost_by_year || []).map((val, idx) => (
                  <circle
                    key={idx}
                    cx={xFor(idx)}
                    cy={yFor(val)}
                    r={hoveredIndex === idx ? 4 : 2}
                    fill={lineColors[v.fuel_type] || COLORS.slate}
                  />
                ))}
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
