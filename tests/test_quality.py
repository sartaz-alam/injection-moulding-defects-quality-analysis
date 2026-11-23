import pytest
from src.quality_analysis import calculate_cp_cpk, conformance_summary, defect_analysis
import pandas as pd


def test_cp_cpk_calculation():
    values = [100, 100.02, 99.98, 100.01, 99.99]
    result = calculate_cp_cpk(values, 99.8, 100.2)
    assert result["cp"] > 0
    assert result["cpk"] > 0


def test_conformance_summary():
    df = pd.DataFrame({
        "Length_mm": [100.0, 100.25],
        "Width_mm": [50.0, 50.0],
        "Thickness_mm": [3.0, 3.0],
        "Diameter_mm": [20.0, 20.0],
    })
    result = conformance_summary(df, {"Length_mm": (99.8, 100.2), "Width_mm": (49.8, 50.2), "Thickness_mm": (2.85, 3.15), "Diameter_mm": (19.8, 20.2)})
    assert result["Length_mm"]["conforming"] == 1
    assert result["Length_mm"]["yield_percent"] == 50.0


def test_defect_pareto():
    df = pd.DataFrame({"Defect_Type": ["Flash", "Flash", "Warpage"], "Defect_Count": [2, 1, 3]})
    result = defect_analysis(df)
    assert result.loc["Warpage", "count"] == 3
    assert pytest.approx(result["cumulative_percentage"].iloc[-1]) == 100
