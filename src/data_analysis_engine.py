"""
Anjiru.AI Structured Data Analysis & Plotting Engine
Parses CSV files, computes statistical distributions, and generates publication-grade Matplotlib plots.
"""

import os
import csv
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
import matplotlib
matplotlib.use('Agg')  # Headless backend for web server environments
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = PROJECT_ROOT / "workspace" / "projects" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


class AnjiruDataAnalyzer:
    """Parses tabular CSV datasets and generates statistical graphs."""

    def __init__(self):
        # Configure professional dark theme matching Anjiru IDE
        plt.rcParams['font.sans-serif'] = 'DejaVu Sans', 'Arial'
        plt.rcParams['axes.edgecolor'] = '#334155'
        plt.rcParams['axes.linewidth'] = 0.8

    def parse_csv(self, file_path_str: str) -> Dict[str, Any]:
        """Parses CSV, identifies column types, and calculates summary metrics."""
        path = Path(file_path_str)
        if not path.exists():
            return {"status": "error", "message": f"CSV file '{file_path_str}' not found."}

        rows: List[Dict[str, str]] = []
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            for r in reader:
                rows.append(r)

        if not rows:
            return {"status": "error", "message": "CSV file is empty."}

        columns_data: Dict[str, List[Any]] = {k: [] for k in fieldnames}
        numeric_stats: Dict[str, Dict[str, float]] = {}

        for r in rows:
            for k in fieldnames:
                val_str = r.get(k, "").strip()
                try:
                    num_val = float(val_str)
                    columns_data[k].append(num_val)
                except ValueError:
                    columns_data[k].append(val_str)

        # Compute summary statistics on numeric columns
        for k in fieldnames:
            vals = columns_data[k]
            num_vals = [v for v in vals if isinstance(v, (int, float)) and not math.isnan(v)]
            if len(num_vals) > len(vals) * 0.7:  # Predominantly numeric
                arr = np.array(num_vals, dtype=float)
                numeric_stats[k] = {
                    "count": int(len(arr)),
                    "mean": round(float(np.mean(arr)), 3),
                    "std": round(float(np.std(arr)), 3),
                    "min": round(float(np.min(arr)), 3),
                    "max": round(float(np.max(arr)), 3),
                    "median": round(float(np.median(arr)), 3),
                    "q25": round(float(np.percentile(arr, 25)), 3),
                    "q75": round(float(np.percentile(arr, 75)), 3)
                }

        return {
            "status": "success",
            "file_name": path.name,
            "row_count": len(rows),
            "column_count": len(fieldnames),
            "columns": fieldnames,
            "numeric_columns": list(numeric_stats.keys()),
            "statistics": numeric_stats,
            "preview": rows[:5]
        }

    def generate_chart(
        self,
        file_path_str: str,
        chart_type: str = "line",
        x_col: Optional[str] = None,
        y_cols: Optional[List[str]] = None,
        title: Optional[str] = None,
        output_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates publication-quality charts from CSV data."""
        parsed = self.parse_csv(file_path_str)
        if parsed.get("status") != "success":
            return parsed

        cols = parsed["columns"]
        numeric_cols = parsed["numeric_columns"]

        if not numeric_cols:
            return {"status": "error", "message": "No numeric columns available in CSV for plotting."}

        # Auto-pick columns if not specified
        if not x_col:
            x_col = cols[0]
        if not y_cols:
            y_cols = [c for c in numeric_cols if c != x_col][:3]
            if not y_cols:
                y_cols = [numeric_cols[0]]

        # Read values from CSV
        rows: List[Dict[str, str]] = []
        with open(file_path_str, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)

        x_vals = []
        y_series = {col: [] for col in y_cols}

        for r in rows:
            x_raw = r.get(x_col, "")
            try:
                x_vals.append(float(x_raw))
            except ValueError:
                x_vals.append(x_raw)

            for col in y_cols:
                try:
                    y_series[col].append(float(r.get(col, 0)))
                except ValueError:
                    y_series[col].append(0.0)

        # Create Plot with VS Code Dark Styling
        fig, ax = plt.subplots(figsize=(9, 5), facecolor='#0b0f17')
        ax.set_facecolor('#0f172a')

        colors = ['#10b981', '#38bdf8', '#f59e0b', '#ec4899', '#a855f7']

        chart_type = chart_type.lower()
        if chart_type == "bar":
            indices = np.arange(len(x_vals[:20]))
            width = 0.8 / len(y_cols)
            for i, col in enumerate(y_cols):
                ax.bar(indices + i * width, y_series[col][:20], width, label=col, color=colors[i % len(colors)], alpha=0.9)
            if all(isinstance(x, str) for x in x_vals[:20]):
                ax.set_xticks(indices + width * (len(y_cols) - 1) / 2)
                ax.set_xticklabels([str(x)[:12] for x in x_vals[:20]], rotation=30, ha='right', color='#94a3b8', fontsize=9)
        elif chart_type == "scatter":
            for i, col in enumerate(y_cols):
                ax.scatter(x_vals, y_series[col], label=col, color=colors[i % len(colors)], alpha=0.8, s=40, edgecolors='none')
        elif chart_type == "histogram":
            for i, col in enumerate(y_cols):
                ax.hist(y_series[col], bins=15, label=col, color=colors[i % len(colors)], alpha=0.6, edgecolor='#334155')
        else:  # line plot default
            for i, col in enumerate(y_cols):
                ax.plot(x_vals, y_series[col], label=col, color=colors[i % len(colors)], linewidth=2.2, marker='o' if len(x_vals) <= 20 else None, markersize=4)

        chart_title = title or f"{chart_type.title()} Chart: {', '.join(y_cols)} vs {x_col}"
        ax.set_title(chart_title, color='#f8fafc', fontsize=13, fontweight='bold', pad=14)
        ax.set_xlabel(str(x_col), color='#94a3b8', fontsize=10.5, labelpad=8)
        ax.set_ylabel("Value", color='#94a3b8', fontsize=10.5, labelpad=8)

        # Ticks and Grid
        ax.tick_params(colors='#94a3b8', labelsize=9)
        ax.grid(True, linestyle='--', alpha=0.25, color='#475569')

        # Legend
        leg = ax.legend(facecolor='#1e293b', edgecolor='#334155', labelcolor='#e2e8f0', fontsize=9.5)
        for text in leg.get_texts():
            text.set_color('#e2e8f0')

        plt.tight_layout()

        # Save to workspace/projects/plots/
        slug = "".join(c if c.isalnum() else "_" for c in (output_name or chart_title)[:24]).strip("_").lower()
        filename = f"plot_{slug}.png"
        output_path = PLOTS_DIR / filename
        fig.savefig(str(output_path), dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)

        return {
            "status": "success",
            "chart_type": chart_type,
            "title": chart_title,
            "x_column": x_col,
            "y_columns": y_cols,
            "file_name": filename,
            "file_path": str(output_path),
            "url": f"/api/plots/view?file={filename}",
            "size_bytes": os.path.getsize(str(output_path)),
            "summary_stats": {c: parsed["statistics"].get(c, {}) for c in y_cols}
        }


# Global singleton
_data_analyzer = None

def get_data_analyzer() -> AnjiruDataAnalyzer:
    global _data_analyzer
    if _data_analyzer is None:
        _data_analyzer = AnjiruDataAnalyzer()
    return _data_analyzer
