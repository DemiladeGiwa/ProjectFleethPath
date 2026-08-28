import React, { useState } from "react";
import { COLORS } from "./styles";
import WizardSteps from "./components/WizardSteps";
import ResultsView from "./components/ResultsView";

const API_URL = "http://localhost:8000/api/v1/calculate";
const REPORT_URL = "http://localhost:8000/api/v1/report";

export default function FleetPathWizard() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    state_prov: "",
    vehicle_type: "school_bus_typeC",
    vehicle_count: 10,
    annual_mileage_per_vehicle: 12000,
    lifecycle_years: 12,
    electricity_rate_kwh: "",
    diesel_price_gal: "",
    incentive_credits_usd: "",
    cold_climate_flag: null,
    cost_carbon_weight: null,
  });
  const [result, setResult] = useState(null);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function toNullableFloat(value) {
    if (value === "" || value === null || value === undefined) return null;
    const parsed = parseFloat(value);
    return Number.isNaN(parsed) ? null : parsed;
  }

  function buildCalculationPayload() {
    const region = { state_prov: form.state_prov };
    const fleet = {
      vehicle_type: form.vehicle_type,
      vehicle_count: Number(form.vehicle_count),
      annual_mileage_per_vehicle: Number(form.annual_mileage_per_vehicle),
      lifecycle_years: Number(form.lifecycle_years),
    };
    const overrides = {
      electricity_rate_kwh: toNullableFloat(form.electricity_rate_kwh),
      diesel_price_gal: toNullableFloat(form.diesel_price_gal),
      incentive_credits_usd: toNullableFloat(form.incentive_credits_usd),
      cost_carbon_weight: form.cost_carbon_weight,
    };
    const climate = { cold_climate_flag: form.cold_climate_flag };

    return { region, fleet, overrides, climate };
  }

  async function submitFleet() {
    setLoading(true);
    setError(null);
    const payload = buildCalculationPayload();

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        let errMsg = "Calculation failed";
        try {
          const body = await response.json();
          if (body.detail) {
            if (typeof body.detail === "string") {
              errMsg = body.detail;
            } else if (Array.isArray(body.detail)) {
              errMsg = body.detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
            } else {
              errMsg = JSON.stringify(body.detail);
            }
          }
        } catch (_) {
          errMsg = `Calculation failed (status ${response.status}): ${response.statusText}`;
        }
        throw new Error(errMsg);
      }
      const data = await response.json();
      setResult(data);
      setStep(4);
    } catch (err) {
      if (err.name === "TypeError" || err.message?.includes("fetch") || err.message?.includes("NetworkError")) {
        setError("Unable to reach the calculation service. Please verify that the backend server is running on port 8000.");
      } else {
        setError(err.message || "An unexpected error occurred during calculation.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function downloadPdfReport() {
    if (!result) return;
    setPdfLoading(true);
    setPdfError(null);
    const payload = buildCalculationPayload();

    try {
      const response = await fetch(REPORT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        let errMsg = "Failed to download PDF report";
        try {
          const body = await response.json();
          if (body.detail) {
            if (typeof body.detail === "string") {
              errMsg = body.detail;
            } else if (Array.isArray(body.detail)) {
              errMsg = body.detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
            } else {
              errMsg = JSON.stringify(body.detail);
            }
          }
        } catch (_) {
          errMsg = `Download failed with status ${response.status}: ${response.statusText}`;
        }
        throw new Error(errMsg);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `fleetpath_report_${form.state_prov}.pdf`);
      document.body.appendChild(link);
      link.click();
      if (link.parentNode) {
        link.parentNode.removeChild(link);
      }
      window.URL.revokeObjectURL(url);
    } catch (err) {
      if (err.name === "TypeError" || err.message?.includes("fetch") || err.message?.includes("NetworkError")) {
        setPdfError("Unable to reach the report service. Please verify that the backend server is running on port 8000.");
      } else {
        setPdfError(err.message || "Failed to download PDF report.");
      }
    } finally {
      setPdfLoading(false);
    }
  }

  function handleStartNew() {
    setStep(1);
    setForm({
      state_prov: "",
      vehicle_type: "school_bus_typeC",
      vehicle_count: 10,
      annual_mileage_per_vehicle: 12000,
      lifecycle_years: 12,
      electricity_rate_kwh: "",
      diesel_price_gal: "",
      incentive_credits_usd: "",
      cold_climate_flag: null,
      cost_carbon_weight: null,
    });
    setResult(null);
    setAdvancedOpen(false);
    setError(null);
    setPdfError(null);
    setPdfLoading(false);
  }

  function handleEditInputs() {
    setError(null);
    setPdfError(null);
    setStep(3);
  }

  const stepsList = [
    { num: 1, label: "Jurisdiction" },
    { num: 2, label: "Fleet Profile" },
    { num: 3, label: "Financials" },
    { num: 4, label: "Decision Matrix" },
  ];

  return (
    <div
      style={{
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        maxWidth: 780,
        margin: "0 auto",
        padding: "36px 20px",
        color: COLORS.navyDark,
        backgroundColor: "#FFFFFF",
        minHeight: "100vh",
      }}
    >
      <style>{`
        input:focus, select:focus, button:focus, summary:focus {
          outline: 2px solid ${COLORS.navy} !important;
          outline-offset: 2px !important;
        }
        @keyframes fp-spinner {
          to { transform: rotate(360deg); }
        }
        .fp-spinner {
          display: inline-block;
          width: 12px;
          height: 12px;
          border: 2px solid currentColor;
          border-top-color: transparent;
          border-radius: 50%;
          animation: fp-spinner 0.6s linear infinite;
          vertical-align: middle;
        }
      `}</style>

      <div style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: "50%",
              backgroundColor: COLORS.emerald,
            }}
          />
          <h1
            style={{
              fontSize: 22,
              fontWeight: 800,
              letterSpacing: "-0.02em",
              color: COLORS.navy,
              margin: 0,
            }}
          >
            FleetPath
          </h1>
          <span
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: COLORS.slateMuted,
              background: COLORS.bgLight,
              border: `1px solid ${COLORS.grayBorder}`,
              padding: "2px 6px",
              borderRadius: 3,
              fontFamily: "ui-monospace, monospace",
            }}
          >
            v1.5
          </span>
        </div>
        <p style={{ fontSize: 13, color: COLORS.slateMuted, margin: 0 }}>
          Independent fuel pathway total cost of ownership and carbon verdict engine for public-sector fleets.
        </p>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginTop: 20,
            borderBottom: `1px solid ${COLORS.grayBorder}`,
            paddingBottom: 12,
            gap: 16,
            overflowX: "auto",
          }}
        >
          {stepsList.map((s) => {
            const isCurrent = step === s.num;
            const isPast = step > s.num;
            return (
              <div
                key={s.num}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 12,
                  fontWeight: isCurrent ? 700 : 500,
                  color: isCurrent ? COLORS.navy : isPast ? COLORS.emeraldDark : COLORS.slateLight,
                  whiteSpace: "nowrap",
                }}
              >
                <span
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: "50%",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 11,
                    fontWeight: 700,
                    backgroundColor: isCurrent
                      ? COLORS.navy
                      : isPast
                      ? COLORS.emeraldBg
                      : COLORS.bgLight,
                    color: isCurrent ? "#FFFFFF" : isPast ? COLORS.emeraldDark : COLORS.slateMuted,
                    border: `1px solid ${
                      isCurrent
                        ? COLORS.navy
                        : isPast
                        ? COLORS.emeraldBorder
                        : COLORS.grayBorder
                    }`,
                  }}
                >
                  {isPast ? "✓" : s.num}
                </span>
                <span>{s.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {step < 4 ? (
        <WizardSteps
          step={step}
          setStep={setStep}
          form={form}
          updateField={updateField}
          submitFleet={submitFleet}
          loading={loading}
          error={error}
        />
      ) : (
        result && (
          <ResultsView
            result={result}
            advancedOpen={advancedOpen}
            setAdvancedOpen={setAdvancedOpen}
            downloadPdfReport={downloadPdfReport}
            pdfLoading={pdfLoading}
            pdfError={pdfError}
            onEditInputs={handleEditInputs}
            onStartNew={handleStartNew}
          />
        )
      )}
    </div>
  );
}
