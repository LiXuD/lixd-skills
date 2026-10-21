#!/usr/bin/env python3
"""
Aggregate answered-call statistics from monthly report workbooks.

Usage:
    python aggregate_calls.py --start "2026-03-26" --end "2026-06-25" --output summary.xlsx
    python aggregate_calls.py --files mar.xlsx apr.xlsx may.xlsx jun.xlsx --start "2026-03-26" --end "2026-06-25" --output summary.xlsx
"""

import argparse
import os
import re
from datetime import datetime, timedelta
from glob import glob

import pandas as pd
from openpyxl import load_workbook
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.label import DataLabelList


DEFAULT_ROOT = os.environ.get("MR_ROOT") or os.getcwd()
SHEET_NAME = "接听电话详情"


def discover_files(root: str, start: datetime, end: datetime):
    """Find monthly workbook files that overlap with the requested date range."""
    files = []
    for year in range(start.year, end.year + 1):
        for month in range(1, 13):
            if year == start.year and month < start.month:
                continue
            if year == end.year and month > end.month:
                continue
            pattern = os.path.join(root, f"{year % 100}年{month}月", f"附件1《{year % 100}年{month}月报统计数据记录表》.xlsx")
            found = glob(pattern)
            if found:
                files.append((found[0], year, month))
    return sorted(files, key=lambda x: (x[1], x[2]))


def parse_chinese_date(x, year, month):
    if pd.isna(x):
        return None
    m = re.match(r"(\d{1,2})月(\d{1,2})号?", str(x).strip())
    if m:
        return datetime(year, int(m.group(1)), int(m.group(2)))
    return None


def aggregate(files, start, end):
    all_rows = []
    for path, year, month in files:
        df = pd.read_excel(path, sheet_name=SHEET_NAME, header=0)
        df["日期"] = df.iloc[:, 0].apply(lambda x: parse_chinese_date(x, year, month))
        df = df[df["日期"].notna()].copy()
        df = df[(df["日期"] >= start) & (df["日期"] <= end)].copy()
        df["月份"] = df["日期"].dt.to_period("M").astype(str)
        if not df.empty:
            all_rows.append(df)

    if not all_rows:
        return None

    combined = pd.concat(all_rows, ignore_index=True)
    numeric_cols = [c for c in combined.select_dtypes(include="number").columns if c not in ("日期",)]

    summary = combined[numeric_cols].sum().astype(int).sort_values(ascending=False)
    summary_df = pd.DataFrame({
        "类别": summary.index,
        "数量": summary.values,
        "占比": (summary.values / summary.sum() * 100).round(2),
    })

    monthly = combined.groupby("月份")[numeric_cols].sum().astype(int)
    monthly["总计"] = monthly.sum(axis=1)
    monthly = monthly.sort_index()

    return combined, summary_df, monthly


def write_excel(summary_df, monthly, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="分类汇总", index=False)
        monthly.to_excel(writer, sheet_name="月度明细")

    wb = load_workbook(output_path)
    ws = wb["分类汇总"]
    chart = PieChart()
    chart.title = "接听电话分类占比"
    chart.height = 10
    chart.width = 15
    labels = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
    data = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labels)
    chart.dataLabels = DataLabelList()
    chart.dataLabels.showPercent = True
    ws.add_chart(chart, "E2")
    wb.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Aggregate monthly call statistics.")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", required=True, help="Output Excel path")
    parser.add_argument("--files", nargs="+", help="Explicit monthly Excel file paths")
    parser.add_argument("--root", default=DEFAULT_ROOT, help=f"Project root (default: {DEFAULT_ROOT})")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d")

    if args.files:
        files = []
        for path in args.files:
            # Attempt to infer year/month from filename or parent directory
            m = re.search(r"26年(\d+)月", path)
            if m:
                month = int(m.group(1))
                year = 2026
            else:
                m = re.search(r"(\d{4})年(\d+)月", path)
                if m:
                    year = int(m.group(1))
                    month = int(m.group(2))
                else:
                    raise ValueError(f"Cannot infer year/month from path: {path}")
            files.append((path, year, month))
    else:
        files = discover_files(args.root, start, end)

    if not files:
        raise SystemExit("No monthly workbook files found for the requested range.")

    result = aggregate(files, start, end)
    if result is None:
        raise SystemExit("No data in the requested range.")

    combined, summary_df, monthly = result
    write_excel(summary_df, monthly, args.output)

    total = summary_df["数量"].sum()
    print(f"统计周期: {args.start} 至 {args.end}")
    print(f"有效天数: {combined['日期'].nunique()}")
    print(f"总接听电话数: {total}")
    print(summary_df.to_string(index=False))
    print(f"\n已输出: {args.output}")


if __name__ == "__main__":
    main()
