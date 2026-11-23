import os
import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt

from src.quality_analysis import (
    load_and_validate, descriptive_statistics, capability_summary,
    defect_analysis, process_correlations, conformance_summary, DIMENSIONS
)


def build_report(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    stats_data = descriptive_statistics(df)
    capability = capability_summary(df)
    defects = defect_analysis(df)
    correlations = process_correlations(df)
    conformance = conformance_summary(df)

    summary = {
        "total_observations": len(df),
        "batches": int(df["Batch_ID"].nunique()),
        "descriptive_statistics": stats_data,
        "process_capability": capability,
        "defects": defects.to_dict("index"),
        "correlations": correlations,
        "conformance": conformance,
    }

    with open(os.path.join(output_dir, "quality_summary.json"), "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    lines = [
        "# Injection Moulding Quality Analysis Report",
        "",
        f"- Total observations: {len(df)}",
        f"- Unique batches: {df['Batch_ID'].nunique()}",
        "",
        "## Dimensional conformance",
        "",
        "| Dimension | Conforming | Nonconforming | Yield | Cpk | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for dimension in DIMENSIONS:
        c = conformance[dimension]
        cap = capability[dimension]
        lines.append(f"| {dimension} | {c['conforming']} | {c['nonconforming']} | {c['yield_percent']}% | {cap['cpk']} | {cap['status']} |")

    lines += ["", "## Defect Pareto", ""]
    for defect, row in defects.iterrows():
        lines.append(f"- {defect}: {int(row['count'])} ({row['percentage']:.2f}%; cumulative {row['cumulative_percentage']:.2f}%)")

    lines += ["", "## Process correlations with defect count", ""]
    for parameter, values in correlations.items():
        lines.append(f"- {parameter}: r = {values['r']}, p = {values['p_value']}")

    lines += [
        "", "## Recommended actions", "",
        "1. Investigate dimensions or defect families with the lowest yield or capability.",
        "2. Confirm SPC stability before using Cpk for process acceptance.",
        "3. Verify gauge repeatability and reproducibility, especially for marginal dimensions.",
        "4. Prioritize mould maintenance and process optimization by Pareto rank.",
        "5. Stratify recurring defects by cavity, machine, material, batch, and shift.",
    ]
    with open(os.path.join(output_dir, "quality_report.md"), "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return summary


def create_charts(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    defects = defect_analysis(df)
    plt.figure(figsize=(10, 5))
    plt.bar(defects.index.astype(str), defects["count"])
    plt.xticks(rotation=35, ha="right")
    plt.title("Injection Moulding Defect Pareto")
    plt.xlabel("Defect type")
    plt.ylabel("Defect count")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "defect_pareto.png"), dpi=150)
    plt.close()

    df[DIMENSIONS].hist(figsize=(12, 8), bins=20, edgecolor="black")
    plt.suptitle("Dimensional Distributions", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "dimension_histograms.png"), dpi=150)
    plt.close()

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for axis, dimension in zip(axes.flat, DIMENSIONS):
        axis.hist(df[dimension], bins=20, edgecolor="black", alpha=0.75)
        axis.axvline(df[dimension].mean(), color="red", linestyle="--", label="Mean")
        axis.set_title(dimension)
        axis.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "dimension_distributions.png"), dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Analyse injection-moulding quality data")
    parser.add_argument("--input", default="data/plastic_components.csv")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    df = load_and_validate(args.input)
    summary = build_report(df, args.output_dir)
    create_charts(df, args.output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
