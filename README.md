# Injection Moulding Defects and Dimensional Quality Control

A Python data-analysis project for identifying injection-moulding defects, investigating their likely process causes, and evaluating dimensional quality using statistical process control (SPC).

## Project overview

The project analyses part measurements and defect observations collected across moulded production batches. It calculates control-chart limits, capability indices, defect rates, and correlations between process parameters and defects.

### Defects analysed

- Short shot
- Flash
- Sink marks
- Warpage
- Burn marks
- Bubbles / voids
- Weld lines
- Flow marks
- Discolouration

### Dimensions analysed

- Length
- Width
- Thickness
- Diameter

## Repository structure

```text
data/plastic_components.csv  Sample production dataset
src/quality_analysis.py      Analysis functions
main.py                      Command-line analysis pipeline
app.py                       Streamlit interactive dashboard
tests/test_quality.py        Unit tests
outputs/                     Generated charts and reports
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the analysis

```bash
python main.py --input data/plastic_components.csv --output-dir outputs
```

The pipeline creates:

- `outputs/quality_summary.json`
- `outputs/quality_report.md`
- Dimension histograms
- Defect Pareto chart
- X-bar control charts
- SPC process capability summary

Launch the optional dashboard:

```bash
streamlit run app.py
```

## Statistical methods

- Descriptive statistics: mean, standard deviation, minimum, maximum
- Pooled process capability: `Cp = (USL - LSL) / (6σ)`
- Capability performance: `Cpk = min((USL - mean)/(3σ), (mean - LSL)/(3σ))`
- Process status: CP/CPK thresholds of 1.33 (capable), 1.00 (marginal), and below 1.00 (incapable)
- Defect Pareto analysis by defect frequency
- Pearson correlation between process parameters and defect count

> Cp and Cpk are best interpreted when the process is statistically stable and observations are approximately normally distributed. Cpk must not be used as the sole basis for acceptance decisions.

## Dataset and assumptions

The included CSV is synthetic but realistic, created for educational and demonstration purposes. Replace it with production inspection data without changing the required column names.

## Suggested data columns

| Column | Example | Purpose |
|---|---|---|
| Batch_ID | B001 | Traceability |
| Length_mm | 100.12 | Dimensional SPC |
| Width_mm | 50.08 | Dimensional SPC |
| Thickness_mm | 3.02 | Dimensional SPC |
| Diameter_mm | 19.96 | Dimensional SPC |
| Melt_Temp_C | 215.4 | Process parameter |
| Injection_Pressure_bar | 94.3 | Process parameter |
| Cycle_Time_s | 24.8 | Process parameter |
| Cooling_Time_s | 12.1 | Process parameter |
| Cavity | 1 | Tool location |
| Machine | M1 | Production machine |
| Material | PP | Polymer grade |
| Defect_Type | Sink marks | Defect classification |
| Defect_Count | 1 | Defect quantity |

## Quality-control recommendations

1. Verify control-chart signals against measurement-system capability.
2. Calibrate gauges and conduct Gage R&R before changing specifications or process settings.
3. Prioritize defect families using Pareto analysis and defect cost.
4. Use subgroup data and reaction plans for real-time SPC.
5. Investigate tool wear, vent blockage, mould temperature, and material moisture for recurring moulding defects.

## License

MIT License
