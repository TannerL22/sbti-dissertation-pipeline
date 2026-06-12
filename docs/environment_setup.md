# Environment Setup

## Python Version

Use Python 3.11 or newer. The current local runs used Python 3.14.

## Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Required Packages

The core requirements are listed in `requirements.txt`.

## Troubleshooting

- If Excel loading fails, confirm `openpyxl` is installed.
- If Parquet loading fails, confirm `pyarrow` is installed.
- If regressions fail, confirm `statsmodels` is installed.
- If plots fail, confirm `matplotlib` is installed.
- If tests cannot find generated outputs, run the relevant pipeline mode first or run `python validate_project.py` to identify missing files.
