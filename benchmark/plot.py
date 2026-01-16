import csv
import argparse
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

# Catppuccin import
import catppuccin
from catppuccin.extras.matplotlib import load_color

# ------------------------------------------------------------------------------
# Args & Theme Selection
# ------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Plot Python vs Cython benchmarks")
parser.add_argument("--dark", action="store_true", help="Use dark theme")
args = parser.parse_args()

# Choose Catppuccin flavor based on --dark flag
if args.dark:
    FLAVOR = catppuccin.PALETTE.mocha
else:
    FLAVOR = catppuccin.PALETTE.frappe

matplotlib.style.use(FLAVOR.identifier)

# ------------------------------------------------------------------------------
# Extract Theme Colors
# ------------------------------------------------------------------------------

py_color = load_color(FLAVOR.identifier, "red")
cy_color = load_color(FLAVOR.identifier, "blue")

# ------------------------------------------------------------------------------
# Load CSV
# ------------------------------------------------------------------------------

sizes_labels = []
py_add, cy_add = [], []
py_sub, cy_sub = [], []
py_matmul, cy_matmul = [], []


def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


with open("benchmark_results.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        size_label = row["Size"]
        sizes_labels.append(size_label)

        py_add.append(parse_float(row.get("ADD_Py_ns")))
        cy_add.append(parse_float(row.get("ADD_Cy_ns")))
        py_sub.append(parse_float(row.get("SUB_Py_ns")))
        cy_sub.append(parse_float(row.get("SUB_Cy_ns")))
        py_matmul.append(parse_float(row.get("MATMUL_Py_ns")))
        cy_matmul.append(parse_float(row.get("MATMUL_Cy_ns")))

# ------------------------------------------------------------------------------
# Sort by number of rows (N)
# ------------------------------------------------------------------------------

def extract_n(label):
    try:
        n = int(label.split("x")[0])
        return n
    except Exception:
        return 0


sorted_indices = np.argsort([extract_n(lbl) for lbl in sizes_labels])
sizes_labels = [sizes_labels[i] for i in sorted_indices]
py_add = [py_add[i] for i in sorted_indices]
cy_add = [cy_add[i] for i in sorted_indices]
py_sub = [py_sub[i] for i in sorted_indices]
cy_sub = [cy_sub[i] for i in sorted_indices]
py_matmul = [py_matmul[i] for i in sorted_indices]
cy_matmul = [cy_matmul[i] for i in sorted_indices]

# ------------------------------------------------------------------------------
# Plot bar chart
# ------------------------------------------------------------------------------

x = np.arange(len(sizes_labels))
width = 0.35

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.subplots_adjust(wspace=3)

ops = [
    ("ADD", py_add, cy_add),
    ("SUB", py_sub, cy_sub),
    ("MATMUL", py_matmul, cy_matmul),
]

for ax, (label, py_vals, cy_vals) in zip(axes, ops):

    ax.bar(x - width / 2, py_vals, width, color=py_color, label="Python")
    ax.bar(x + width / 2, cy_vals, width, color=cy_color, label="Cython")

    ax.set_xticks(x)
    ax.set_xticklabels(sizes_labels, rotation=45, ha="right", fontsize=8)
    ax.set_yscale("log")

    ax.set_title(label, fontsize=12)

    ax.set_xlabel("Matrix Sizes (N x M)", fontsize=12, labelpad=15)
    ax.set_ylabel("Time (ns)", fontsize=12, labelpad=5)

    ax.grid(True, alpha=0.4, linestyle="--", linewidth=0.8)

    legend = ax.legend(
        frameon=True,
        fancybox=True,
        borderaxespad=1,
        loc="best",
    )
    for lh in legend.get_lines():
        lh.set_linewidth(0.5)

    legend.get_frame().set_linewidth(0.5)

plt.suptitle(
    "Python vs Cython Execution Time",
    fontsize=16,
)

# Subtitle
fig.text(
    0.5,
    0.93,
    "(Lower is better)",
    ha="center",
    fontsize=10,
)

plt.tight_layout()
plt.show()
