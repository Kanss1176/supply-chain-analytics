"""Print the real codes found in the downloaded M3 data, so we can map them to industries.

Run:    python pepsico_planning/explore_m3.py
Output: printed on screen and saved to data/explore_output.txt (send that file or paste it back).
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "m3_raw.csv"
OUT_PATH = ROOT / "data" / "explore_output.txt"


def main() -> None:
    df = pd.read_csv(RAW_PATH, parse_dates=["month"])
    lines = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit(f"Rows: {len(df)}   Months: {df['month'].min():%Y-%m} to {df['month'].max():%Y-%m}")
    emit()
    emit("data_type_code values (row counts):")
    emit(df["data_type_code"].value_counts().to_string())
    emit()
    emit("seasonally_adj values (row counts):")
    emit(df["seasonally_adj"].value_counts().to_string())
    emit()
    emit("error_data values (row counts):")
    emit(df["error_data"].value_counts().to_string())
    emit()

    latest = df[df["value"].notna()]["month"].max()
    emit(f"Latest month with values: {latest:%Y-%m}")
    emit("Latest values by category_code and data_type_code (seasonally_adj as in the file):")
    snap = df[df["month"] == latest]
    table = snap.pivot_table(
        index=["category_code", "seasonally_adj"],
        columns="data_type_code",
        values="value",
        aggfunc="first",
    )
    emit(table.to_string())

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
