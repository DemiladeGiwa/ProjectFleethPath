import React from "react";
import {
  COLORS,
  PATHWAY_LABELS,
  cardStyle,
  cellStyle,
  cellHeaderStyle,
  formatMoney,
  formatTons,
  formatYears,
  formatPct,
} from "../styles";
import StackedBarChart from "./StackedBarChart";
import PaybackLineChart from "./PaybackLineChart";
import AssumptionsMatrix from "./AssumptionsMatrix";

export default function ResultsView({
  result,
  advancedOpen,
  setAdvancedOpen,
  downloadPdfReport,
  pdfLoading,
  pdfError,
  onEditInputs,
  onStartNew,
}) {
  if (!result || !result.verdict || !result.pathways) {
    return null;
  }

  const { verdict, pathways, advanced } = result;
  const currency = pathways[0]?.currency || "USD";
  const winner = verdict.winner_pathway;
  const winnerData = pathways.find((p) => p.fuel_type === winner) || pathways[0];
  const dieselData = pathways.find((p) => p.fuel_type === "diesel") || pathways[0];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div
        style={{
          ...cardStyle,
          borderLeft: `5px solid ${COLORS.emerald}`,
          padding: 24,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            flexWrap: "wrap",
            gap: 12,
            marginBottom: 12,
          }}
        >
          <div>
            <div
              style={{
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: COLORS.emeraldDark,
                marginBottom: 4,
              }}
            >
              Recommended Pathway
            </div>
            <h2
              style={{
                fontSize: 26,
                fontWeight: 800,
                color: COLORS.navy,
                margin: 0,
                lineHeight: 1.2,
              }}
            >
              {PATHWAY_LABELS[winner] || winner}
            </h2>
          </div>

          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.slateMuted, textTransform: "uppercase" }}>
              Lifetime TCO ({currency})
            </div>
            <div
              style={{
                fontSize: 24,
                fontWeight: 800,
                color: COLORS.navyDark,
                fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
              }}
            >
              {formatMoney(winnerData?.tco_total, currency)}
            </div>
          </div>
        </div>

        <p
          style={{
            fontSize: 14,
            lineHeight: 1.5,
            color: COLORS.slate,
            margin: "0 0 20px 0",
            maxWidth: 640,
          }}
        >
          {verdict.summary_text}
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
            gap: 12,
            paddingTop: 16,
            borderTop: `1px solid ${COLORS.grayBorder}`,
            marginBottom: 20,
          }}
        >
          <div style={{ background: COLORS.bgLight, padding: "10px 12px", borderRadius: 4 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.slateMuted, textTransform: "uppercase" }}>
              Payback vs Diesel
            </div>
            <div style={{ fontSize: 15, fontWeight: 700, color: COLORS.navyDark, marginTop: 2 }}>
              {formatYears(verdict.payback_years)}
            </div>
          </div>

          <div style={{ background: COLORS.bgLight, padding: "10px 12px", borderRadius: 4 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.slateMuted, textTransform: "uppercase" }}>
              CO2e Reduction
            </div>
            <div
              style={{
                fontSize: 15,
                fontWeight: 700,
                color: verdict.emissions_reduction_pct > 0 ? COLORS.emeraldDark : COLORS.slate,
                marginTop: 2,
              }}
            >
              {formatPct(verdict.emissions_reduction_pct)}
            </div>
          </div>

          <div style={{ background: COLORS.bgLight, padding: "10px 12px", borderRadius: 4 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.slateMuted, textTransform: "uppercase" }}>
              Lifetime Emissions
            </div>
            <div style={{ fontSize: 15, fontWeight: 700, color: COLORS.navyDark, marginTop: 2 }}>
              {formatTons(winnerData?.lifecycle_co2e_tons)}
            </div>
          </div>

          <div style={{ background: COLORS.bgLight, padding: "10px 12px", borderRadius: 4 }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.slateMuted, textTransform: "uppercase" }}>
              Currency Standard
            </div>
            <div style={{ fontSize: 15, fontWeight: 700, color: COLORS.navyDark, marginTop: 2 }}>
              {currency} Native
            </div>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <button
              onClick={downloadPdfReport}
              disabled={pdfLoading}
              style={{
                background: pdfLoading ? "#94A3B8" : COLORS.navy,
                border: "none",
                color: "#FFFFFF",
                padding: "8px 16px",
                borderRadius: 4,
                fontSize: 13,
                fontWeight: 600,
                cursor: pdfLoading ? "not-allowed" : "pointer",
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              {pdfLoading && <span className="fp-spinner" aria-hidden="true" />}
              {pdfLoading ? "Generating Report..." : "Download PDF Audit Report"}
            </button>
            <button
              onClick={onEditInputs}
              style={{
                background: "#FFFFFF",
                border: `1px solid ${COLORS.grayBorderDark}`,
                color: COLORS.slate,
                padding: "8px 14px",
                borderRadius: 4,
                fontSize: 13,
                fontWeight: 500,
                cursor: "pointer",
              }}
            >
              ← Edit Inputs & Overrides
            </button>
          </div>

          <button
            onClick={onStartNew}
            style={{
              background: "none",
              border: "none",
              color: COLORS.slateMuted,
              cursor: "pointer",
              fontSize: 12,
              textDecoration: "underline",
              padding: 0,
            }}
          >
            Start a new calculation
          </button>
        </div>

        {pdfError && (
          <div
            style={{
              background: COLORS.dangerBg,
              border: `1px solid ${COLORS.dangerBorder}`,
              borderLeft: `4px solid ${COLORS.danger}`,
              padding: "10px 14px",
              borderRadius: 4,
              color: COLORS.danger,
              fontSize: 13,
              marginTop: 14,
            }}
          >
            <strong>Report Generation Error:</strong> {pdfError}
          </div>
        )}
      </div>

      <div style={cardStyle}>
        <div style={{ marginBottom: 14 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: COLORS.navy, margin: "0 0 4px 0" }}>
            5-Pathway Decision Matrix
          </h3>
          <p style={{ fontSize: 12, color: COLORS.slateMuted, margin: 0 }}>
            Side-by-side total cost of ownership and carbon comparison against the diesel baseline.
          </p>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, textAlign: "left" }}>
            <thead>
              <tr>
                <th style={{ ...cellHeaderStyle, width: "26%" }}>Fuel Pathway</th>
                <th style={{ ...cellHeaderStyle, width: "22%" }}>Lifetime TCO</th>
                <th style={{ ...cellHeaderStyle, width: "18%" }}>Cost Delta</th>
                <th style={{ ...cellHeaderStyle, width: "18%" }}>Lifecycle CO2e</th>
                <th style={{ ...cellHeaderStyle, width: "16%", textAlign: "center" }}>Verdict</th>
              </tr>
            </thead>
            <tbody>
              {pathways.map((p) => {
                const isWinner = p.fuel_type === winner;
                const isDiesel = p.fuel_type === "diesel";
                const deltaCost = p.tco_total - (dieselData?.tco_total || 0);

                return (
                  <tr
                    key={p.fuel_type}
                    style={{
                      background: isWinner ? COLORS.emeraldBg : "#FFFFFF",
                      borderLeft: isWinner ? `4px solid ${COLORS.emerald}` : "4px solid transparent",
                      borderBottom: `1px solid ${COLORS.grayBorder}`,
                    }}
                  >
                    <td style={cellStyle}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontWeight: isWinner ? 700 : 600, color: COLORS.navyDark }}>
                          {PATHWAY_LABELS[p.fuel_type] || p.fuel_type}
                        </span>
                        {isDiesel && (
                          <span
                            style={{
                              fontSize: 10,
                              color: COLORS.slateMuted,
                              background: COLORS.bgLight,
                              border: `1px solid ${COLORS.grayBorder}`,
                              padding: "1px 4px",
                              borderRadius: 3,
                            }}
                          >
                            Baseline
                          </span>
                        )}
                      </div>
                    </td>
                    <td
                      style={{
                        ...cellStyle,
                        fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                        fontWeight: isWinner ? 700 : 500,
                        color: isWinner ? COLORS.navy : COLORS.navyDark,
                      }}
                    >
                      {formatMoney(p.tco_total, p.currency || currency)}
                    </td>
                    <td
                      style={{
                        ...cellStyle,
                        fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                        fontSize: 12,
                      }}
                    >
                      {isDiesel ? (
                        <span style={{ color: COLORS.slateMuted }}>$0 (Baseline)</span>
                      ) : deltaCost < 0 ? (
                        <span style={{ color: COLORS.emeraldDark, fontWeight: 600 }}>
                          -{formatMoney(Math.abs(deltaCost), p.currency || currency)}
                        </span>
                      ) : (
                        <span style={{ color: COLORS.slateMuted }}>
                          +{formatMoney(deltaCost, p.currency || currency)}
                        </span>
                      )}
                    </td>
                    <td
                      style={{
                        ...cellStyle,
                        fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
                      }}
                    >
                      {formatTons(p.lifecycle_co2e_tons)}
                    </td>
                    <td style={{ ...cellStyle, textAlign: "center" }}>
                      {isWinner ? (
                        <span
                          style={{
                            fontSize: 11,
                            fontWeight: 700,
                            color: COLORS.emeraldDark,
                            background: COLORS.emeraldBg,
                            border: `1px solid ${COLORS.emeraldBorder}`,
                            padding: "2px 8px",
                            borderRadius: 4,
                            display: "inline-block",
                          }}
                        >
                          Winner
                        </span>
                      ) : (
                        <span style={{ color: COLORS.slateLight, fontSize: 12 }}>—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div style={cardStyle}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <div>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: COLORS.navy, margin: "0 0 2px 0" }}>
              Advanced Fiduciary Audit Dashboard
            </h3>
            <p style={{ fontSize: 12, color: COLORS.slateMuted, margin: 0 }}>
              Granular CapEx/OpEx component breakdown, cumulative payback curves, and assumption provenance.
            </p>
          </div>
          <button
            onClick={() => setAdvancedOpen(!advancedOpen)}
            style={{
              background: advancedOpen ? COLORS.bgLight : "#FFFFFF",
              border: `1px solid ${COLORS.navy}`,
              color: COLORS.navy,
              padding: "7px 14px",
              borderRadius: 4,
              cursor: "pointer",
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            {advancedOpen ? "Hide Dashboard ▲" : "Show Dashboard ▼"}
          </button>
        </div>

        {advancedOpen && (
          <div style={{ marginTop: 24, paddingTop: 20, borderTop: `1px solid ${COLORS.grayBorder}` }}>
            <div style={{ marginBottom: 28 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: COLORS.navy, margin: 0 }}>
                  TCO Composition Breakdown
                </h4>
                <span style={{ fontSize: 11, color: COLORS.slateMuted }}>
                  Amortized Vehicle & Infra CapEx + Annualized OpEx ({currency})
                </span>
              </div>
              <StackedBarChart data={advanced?.tco_composition || pathways} />
            </div>

            <div style={{ marginBottom: 28 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: COLORS.navy, margin: 0 }}>
                  Cumulative Payback Trajectory
                </h4>
                <span style={{ fontSize: 11, color: COLORS.slateMuted }}>
                  Cumulative expenditure from Year 0 upfront capital to horizon ({currency})
                </span>
              </div>
              <PaybackLineChart
                vectors={advanced?.payback_vector || []}
                yearsAxis={advanced?.payback_vector_years_axis || []}
              />
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: COLORS.navy, margin: 0 }}>
                  Verifiable Assumptions & Provenance Registry
                </h4>
                <span style={{ fontSize: 11, color: COLORS.slateMuted }}>
                  Individual citations and user overrides by pathway
                </span>
              </div>
              <AssumptionsMatrix pathways={pathways} winnerPathway={winner} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
