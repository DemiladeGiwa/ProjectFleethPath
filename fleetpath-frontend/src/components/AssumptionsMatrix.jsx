import React, { useState } from "react";
import { COLORS, PATHWAY_LABELS, cellStyle, cellHeaderStyle } from "../styles";

export default function AssumptionsMatrix({ pathways, winnerPathway }) {
  const [selectedPathway, setSelectedPathway] = useState(winnerPathway || pathways[0]?.fuel_type || "diesel");

  if (!pathways || pathways.length === 0) {
    return (
      <div style={{ padding: 16, color: COLORS.slateMuted, fontSize: 13, fontStyle: "italic" }}>
        No assumptions tracked for this fleet calculation.
      </div>
    );
  }

  const activePathwayData = pathways.find((p) => p.fuel_type === selectedPathway) || pathways[0];
  const assumptions = activePathwayData.assumptions || [];
  const overrideCount = assumptions.filter((a) => a.is_override).length;

  return (
    <div
      style={{
        marginTop: 14,
        marginBottom: 24,
        border: `1px solid ${COLORS.grayBorder}`,
        borderRadius: 4,
        background: "#FFFFFF",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          background: COLORS.bgLight,
          borderBottom: `1px solid ${COLORS.grayBorder}`,
          padding: "10px 16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 8,
        }}
      >
        <div>
          <span
            style={{
              fontSize: 11,
              fontWeight: 700,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: COLORS.slateMuted,
              fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            }}
          >
            Audit Provenance & Assumptions Registry
          </span>
        </div>
        <div style={{ fontSize: 12, color: COLORS.slateMuted }}>
          Total Cited Parameters: <strong>{assumptions.length}</strong>
          {overrideCount > 0 && (
            <span style={{ marginLeft: 10, color: COLORS.amber, fontWeight: 600 }}>
              ({overrideCount} User {overrideCount === 1 ? "Override" : "Overrides"} Active)
            </span>
          )}
        </div>
      </div>

      <div
        style={{
          display: "flex",
          borderBottom: `1px solid ${COLORS.grayBorder}`,
          background: "#FFFFFF",
          overflowX: "auto",
        }}
      >
        {pathways.map((p) => {
          const isSelected = p.fuel_type === selectedPathway;
          const isWinner = p.fuel_type === winnerPathway;
          return (
            <button
              key={p.fuel_type}
              onClick={() => setSelectedPathway(p.fuel_type)}
              style={{
                padding: "10px 16px",
                border: "none",
                borderBottom: isSelected ? `2px solid ${COLORS.navy}` : "2px solid transparent",
                background: isSelected ? "#FFFFFF" : COLORS.bgLight,
                color: isSelected ? COLORS.navy : COLORS.slateMuted,
                fontWeight: isSelected ? 600 : 500,
                fontSize: 12,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 6,
                whiteSpace: "nowrap",
                fontFamily: "inherit",
              }}
            >
              <span>{PATHWAY_LABELS[p.fuel_type] || p.fuel_type}</span>
              {isWinner && (
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    color: COLORS.emeraldDark,
                    background: COLORS.emeraldBg,
                    border: `1px solid ${COLORS.emeraldBorder}`,
                    padding: "1px 5px",
                    borderRadius: 3,
                  }}
                >
                  Winner
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, textAlign: "left" }}>
          <thead>
            <tr>
              <th style={{ ...cellHeaderStyle, width: "24%" }}>Param ID</th>
              <th style={{ ...cellHeaderStyle, width: "28%" }}>Description / Parameter</th>
              <th style={{ ...cellHeaderStyle, width: "18%" }}>Value & Unit</th>
              <th style={{ ...cellHeaderStyle, width: "20%" }}>Source Authority</th>
              <th style={{ ...cellHeaderStyle, width: "10%", textAlign: "center" }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {assumptions.map((a) => (
              <tr
                key={a.param_id}
                style={{
                  background: a.is_override ? "#FFFDF5" : "#FFFFFF",
                  borderBottom: `1px solid ${COLORS.grayBorder}`,
                }}
              >
                <td
                  style={{
                    ...cellStyle,
                    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                    fontSize: 11,
                    color: COLORS.navy,
                    fontWeight: 600,
                  }}
                >
                  {a.param_id}
                </td>
                <td style={cellStyle}>
                  <div style={{ fontWeight: 500, color: COLORS.navyDark }}>{a.label}</div>
                </td>
                <td
                  style={{
                    ...cellStyle,
                    fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                    fontWeight: 600,
                    color: COLORS.slate,
                  }}
                >
                  {typeof a.value === "number" ? a.value.toLocaleString("en-US") : a.value}
                  {a.unit ? ` ${a.unit}` : ""}
                </td>
                <td style={{ ...cellStyle, color: COLORS.slateMuted, fontSize: 11 }}>
                  {a.source_agency || "—"}
                </td>
                <td style={{ ...cellStyle, textAlign: "center" }}>
                  {a.is_override ? (
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 700,
                        color: "#92400E",
                        background: COLORS.amberBg,
                        border: `1px solid #FDE68A`,
                        padding: "2px 6px",
                        borderRadius: 3,
                        display: "inline-block",
                      }}
                    >
                      Override
                    </span>
                  ) : (
                    <span
                      style={{
                        fontSize: 10,
                        fontWeight: 600,
                        color: COLORS.slateMuted,
                        background: COLORS.bgLight,
                        border: `1px solid ${COLORS.grayBorder}`,
                        padding: "2px 6px",
                        borderRadius: 3,
                        display: "inline-block",
                      }}
                    >
                      Baseline
                    </span>
                  )}
                </td>
              </tr>
            ))}
            {assumptions.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  style={{
                    ...cellStyle,
                    color: COLORS.slateMuted,
                    fontStyle: "italic",
                    textAlign: "center",
                    padding: 24,
                  }}
                >
                  No parameter assumptions logged for this pathway.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div
        style={{
          padding: "8px 16px",
          background: COLORS.bgLight,
          borderTop: `1px solid ${COLORS.grayBorder}`,
          fontSize: 11,
          color: COLORS.slateMuted,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>
          Independent decision-support audit log. All baselines traceable to NREL AFLEET, EPA eGRID, ECCC NIR, or Bank of Canada FX.
        </span>
      </div>
    </div>
  );
}
