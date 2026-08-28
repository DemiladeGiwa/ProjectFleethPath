import urllib.request
import json
import sys

SCENARIOS = {
    "scenario_a_qc_bev": {
        "region": {"state_prov": "QC"},
        "fleet": {
            "vehicle_type": "school_bus_typeC",
            "vehicle_count": 10,
            "annual_mileage_per_vehicle": 12000,
            "lifecycle_years": 12,
        },
        "overrides": {},
        "climate": {},
    },
    "scenario_b_nb_comparison": {
        "region": {"state_prov": "NB"},
        "fleet": {
            "vehicle_type": "school_bus_typeC",
            "vehicle_count": 233,
            "annual_mileage_per_vehicle": 12000,
            "lifecycle_years": 12,
        },
        "overrides": {},
        "climate": {"cold_climate_flag": None},
    },
    "scenario_c_tx_cng": {
        "region": {"state_prov": "TX"},
        "fleet": {
            "vehicle_type": "school_bus_typeC",
            "vehicle_count": 25,
            "annual_mileage_per_vehicle": 15000,
            "lifecycle_years": 10,
        },
        "overrides": {},
        "climate": {},
    },
}


def run_and_save(prefix="baseline"):
    results = {}
    for name, payload in SCENARIOS.items():
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/v1/calculate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            filename = f"{prefix}_{name}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, sort_keys=True)
            results[name] = data
            winner = data["verdict"]["winner_pathway"]
            curr = data["pathways"][0]["currency"]
            print(f"[{prefix}] {name}: saved to {filename} (winner={winner}, currency={curr})")
    return results


def diff_against_baseline(candidate_prefix="candidate", baseline_prefix="baseline"):
    diffs_found = False
    for name in SCENARIOS:
        baseline_file = f"{baseline_prefix}_{name}.json"
        candidate_file = f"{candidate_prefix}_{name}.json"
        with open(baseline_file, "r", encoding="utf-8") as bf, open(candidate_file, "r", encoding="utf-8") as cf:
            base_content = bf.read()
            cand_content = cf.read()
        if base_content == cand_content:
            print(f"DIFF [{name}]: BYTE-IDENTICAL to baseline.")
        else:
            print(f"DIFF [{name}]: MISMATCH DETECTED!")
            diffs_found = True
    return not diffs_found


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if mode == "compare":
        cand = sys.argv[2] if len(sys.argv) > 2 else "candidate"
        base = sys.argv[3] if len(sys.argv) > 3 else "baseline"
        success = diff_against_baseline(cand, base)
        sys.exit(0 if success else 1)
    else:
        run_and_save(mode)

