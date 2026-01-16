## Benchmarking Cython and Python

We benchmark the 3 operations defined : element wise add, element wise subtract and matmul.
These are the basic configurations used :

```json
{
  "configuration": "Non-uniform rectangular sweep (random sizes)",
  "iterations": 8,
  "num_random_sizes": 5,
  "min_dim": 10,
  "max_dim": 300
}
```

where

- `configuration` is either a uniform (N x N) square matrices OR non-uniform (N x M)
  rectangular matrices
- `iterations` is the number of runs we do (to get mean, variance, etc)
- `num_random_sizes` is the number of matrices created
- `min_dim and max_dim` are the min and max dimensions of matrices (randomly chosen)

### Setup and Usage

1. Create `venv` and install the required libraries using `uv` :

   ```bash
       uv venv .venv --python=3.14
       uv sync
   ```

2. Run the benchmarking script : (this will generate a `benchmark_results.csv` file)

   ```bash
       python bench.py
   ```

3. Plot the results :

   ```bash
       python plot.py
   ```

If the `.pyx / .pxd` file are updated, then build it again :

    ```bash
        cd ../peak_utils
        uv build --wheel
    ```

And update it :

    ```bash
        cd ../benchmark
        uv sync

        # If sync doesn't update it, then do :
        uv remove peak_utils

        # and then this : ( [----] is a placeholder )
        uv add ../peak_utils/dist/peak_utils-0.1.0[----].whl
    ```

For development mode, do this instead :

    ```bash
        uv add ../peak_utils --editable
    ```