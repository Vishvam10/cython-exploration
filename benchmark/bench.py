import argparse
import random
import statistics
import csv
import time
import json
from tabulate import tabulate

# ------------------------------------------------------------------------------
# ANSI Colors
# ------------------------------------------------------------------------------


class Colors:
    DARK_GREEN = "\033[42;97m"
    GREEN = "\033[102;30m"
    YELLOW = "\033[103;30m"
    ORANGE = "\033[48;5;214m"
    RED = "\033[101;97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def color_speedup(pct):
    if pct >= 80:
        return Colors.DARK_GREEN
    elif pct >= 60:
        return Colors.GREEN
    elif pct >= 40:
        return Colors.YELLOW
    elif pct >= 20:
        return Colors.ORANGE
    else:
        return Colors.RED


# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------


def make_random_matrix(cls, n, m):
    data = [[random.random() for _ in range(m)] for _ in range(n)]
    return cls.from_list(data)


def benchmark_op(func, iterations=10, warmup=2):
    times = []
    for _ in range(warmup):
        func()
    for _ in range(iterations):
        start = time.perf_counter_ns()
        func()
        end = time.perf_counter_ns()
        times.append(end - start)
    mean = statistics.mean(times)
    var = statistics.variance(times) if len(times) > 1 else 0.0
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    return mean, var, std


def pct_change(base, new):
    return ((base - new) / base) * 100.0


# ------------------------------------------------------------------------------
# Main Benchmark
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import random
    from pymatrix import PyMatrix
    
    from peak_utils import Matrix

    parser = argparse.ArgumentParser(description="Benchmark matrices")
    parser.add_argument(
        "--uniform", action="store_true", help="Run uniform square sweep (powers of 2)"
    )
    args = parser.parse_args()
    random.seed(0)

    # Benchmark configuration
    iterations = 8
    num_random_sizes = 5
    min_dim = 10
    max_dim = 300

    print("\nBenchmark configuration :\n")
    print(
        json.dumps(
            {
                "configuration": "Uniform square sweep (powers of 2 sizes)"
                if args.uniform
                else "Non-uniform rectangular sweep (random sizes)",
                "iterations": iterations,
                "num_random_sizes": num_random_sizes,
                "min_dim": min_dim,
                "max_dim": max_dim,
            },
            indent=2,
        )
    )

    # Prepare matrix sizes
    matrix_sizes = []

    if args.uniform:
        sizes = [16, 32, 64, 128, 256]
        for s in sizes:
            matrix_sizes.append(("ADD/SUB", (s, s), (s, s)))
            matrix_sizes.append(("MATMUL", (s, s), (s, s)))
    else:
        for _ in range(num_random_sizes):
            # ADD/SUB : generate one random valid size
            n, m = random.randint(min_dim, max_dim), random.randint(min_dim, max_dim)
            matrix_sizes.append(("ADD/SUB", (n, m), (n, m)))

            # MATMUL : generate compatible random matrices
            a_rows = random.randint(min_dim, max_dim)
            a_cols = random.randint(min_dim, max_dim)
            b_rows = a_cols
            b_cols = random.randint(min_dim, max_dim)
            matrix_sizes.append(("MATMUL", (a_rows, a_cols), (b_rows, b_cols)))

    # Run benchmarks
    table_rows = []
    csv_rows = []
    all_csv_keys = set(["Size"])
    all_ops = ["ADD", "SUB", "MATMUL"]

    seen_pairs = set()
    for op_type, size_a, size_b in matrix_sizes:
        pair_key = (size_a, size_b)
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)

        # Generate A matrices once per pair
        A_py = make_random_matrix(PyMatrix, *size_a)
        A_cy = make_random_matrix(Matrix, *size_a)

        row_cells = [f"({size_a[0]} x {size_a[1]}) on ({size_b[0]} x {size_b[1]})"]
        csv_row = {"Size": row_cells[0]}

        for op in all_ops:
            # Determine if this op exists for this pair
            entry = next(
                (
                    (t, s_a, s_b)
                    for t, s_a, s_b in matrix_sizes
                    if s_a == size_a
                    and s_b == size_b
                    and (op in ["ADD", "SUB"] if t == "ADD/SUB" else op == "MATMUL")
                ),
                None,
            )

            if entry:
                # Generate B matrices once per operation
                B_py = make_random_matrix(PyMatrix, *size_b)
                B_cy = make_random_matrix(Matrix, *size_b)

                func_py = getattr(A_py, op.lower())
                func_cy = getattr(A_cy, op.lower())

                py_mean, _, _ = benchmark_op(lambda: func_py(B_py), iterations=iterations)
                cy_mean, _, _ = benchmark_op(lambda: func_cy(B_cy), iterations=iterations)

                diff_pct = pct_change(py_mean, cy_mean)
                color = color_speedup(diff_pct)

                py_cell = f"{py_mean:10.0f}"
                if diff_pct > 0:
                    arrow = "↑"
                    cell_color = color
                elif diff_pct < 0:
                    arrow = "↓"
                    cell_color = Colors.RED
                else:
                    arrow = "-"
                    cell_color = Colors.RESET

                cy_cell = (
                    f"{cy_mean:10.0f} ({cell_color}{Colors.BOLD}{arrow}{abs(diff_pct):.1f}%{Colors.RESET})"
                )

                row_cells.extend([py_cell, cy_cell])

                csv_row[f"{op}_Py_ns"] = py_mean
                csv_row[f"{op}_Cy_ns"] = cy_mean
                csv_row[f"{op}_Speedup_%"] = diff_pct
                all_csv_keys.update([f"{op}_Py_ns", f"{op}_Cy_ns", f"{op}_Speedup_%"])
            else:
                row_cells.extend(["-", "-"])

        table_rows.append(row_cells)
        csv_rows.append(csv_row)

    # Print results
    headers = ["Size"]
    for op in all_ops:
        headers.extend([f"Py {op}", f"Cy {op}"])

    print("\nExecution Time (ns) :\n")
    print(tabulate(table_rows, headers=headers, tablefmt="grid"))

    # Save CSV
    fieldnames = list(all_csv_keys)
    with open("benchmark_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\nSaved benchmark_results.csv ✅\n")
