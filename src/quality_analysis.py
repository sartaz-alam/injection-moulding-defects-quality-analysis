import pandas as pd
import numpy as np
from scipy import stats

REQUIRED_COLUMNS = {
    "Batch_ID", "Length_mm", "Width_mm", "Thickness_mm", "Diameter_mm",
    "Melt_Temp_C", "Injection_Pressure_bar", "Cycle_Time_s",
    "Cooling_Time_s", "Cavity", "Machine", "Material",
    "Defect_Type", "Defect_Count"
}

DIMENSIONS = ["Length_mm", "Width_mm", "Thickness_mm", "Diameter_mm"]

DEFAULT_LIMITS = {
    "Length_mm": (99.80, 100.20),
    "Width_mm": (49.80, 50.20),
    "Thickness_mm": (2.85, 3.15),
    "Diameter_mm": (19.80, 20.20),
}


def load_and_validate(path):
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        raise ValueError("Dataset contains no observations")

    for column in DIMENSIONS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["Defect_Count"] = pd.to_numeric(df["Defect_Count"], errors="coerce").fillna(0)

    if df[DIMENSIONS].isna().any().any():
        raise ValueError("Dimension columns contain invalid or missing values")
    return df


def descriptive_statistics(df):
    return df[DIMENSIONS].describe().T.round(4).to_dict("index")


def calculate_cp_cpk(values, lsl, usl):
    values = np.asarray(values, dtype=float)
    sigma = np.std(values, ddof=1)
    mean = np.mean(values)
    if sigma == 0:
        return {"mean": mean, "std_dev": 0.0, "cp": float("inf"),
                "cpk": float("inf")}
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - mean) / (3 * sigma), (mean - lsl) / (3 * sigma))
    return {"mean": round(float(mean), 4), "std_dev": round(float(sigma), 4),
            "cp": round(float(cp), 4), "cpk": round(float(cpk), 4)}


def capability_summary(df, limits=None):
    limits = limits or DEFAULT_LIMITS
    summary = {}
    for dimension, (lsl, usl) in limits.items():
        result = calculate_cp_cpk(df[dimension].dropna(), lsl, usl)
        cpk = result["cpk"]
        if cpk >= 1.33:
            status = "Capable"
        elif cpk >= 1.00:
            status = "Marginal"
        else:
            status = "Incapable"
        result["lsl"] = lsl
        result["usl"] = usl
        result["status"] = status
        summary[dimension] = result
    return summary


def defect_analysis(df):
    defect_counts = df.groupby("Defect_Type", dropna=False)["Defect_Count"].sum().sort_values(ascending=False)
    total = float(defect_counts.sum())
    pareto = pd.DataFrame({
        "count": defect_counts,
        "percentage": defect_counts / total * 100 if total else 0,
    })
    pareto["cumulative_percentage"] = pareto["percentage"].cumsum()
    return pareto


def process_correlations(df):
    process_columns = ["Melt_Temp_C", "Injection_Pressure_bar", "Cycle_Time_s", "Cooling_Time_s"]
    correlations = {}
    for column in process_columns:
        r, p = stats.pearsonr(df[column], df["Defect_Count"])
        correlations[column] = {"r": round(float(r), 4), "p_value": round(float(p), 6)}
    return correlations


def conformance_summary(df, limits=None):
    limits = limits or DEFAULT_LIMITS
    output = {}
    for dimension, (lsl, usl) in limits.items():
        within = df[dimension].between(lsl, usl, inclusive="both")
        count = int(within.sum())
        output[dimension] = {
            "conforming": count,
            "nonconforming": int(len(df) - count),
            "yield_percent": round(count / len(df) * 100, 2)
        }
    return output
