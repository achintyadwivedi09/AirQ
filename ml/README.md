# ML — Smart Air Pollution Monitoring Portal

This folder will contain the forecasting and machine learning components.

## Planned Structure (Future ML Step)

```
ml/
├── notebooks/           # Jupyter notebooks for EDA and model experiments
│   └── 01_eda.ipynb     # Exploratory data analysis on historical readings
├── models/              # Saved trained models
│   └── pm25_arima_delhi.pkl   # Example: ARIMA model for Delhi PM2.5
├── src/
│   ├── train.py         # Model training script
│   ├── predict.py       # Inference script (called by backend)
│   └── preprocess.py    # Data cleaning for model input
└── README.md            # This file
```

## Planned Approach

| Stage | Method |
|---|---|
| Baseline | ARIMA (statsmodels) — simple time-series model |
| Comparison | Random Forest Regressor (scikit-learn) |
| Input | Hourly PM2.5/AQI readings (minimum 30 days) |
| Output | 24-hour ahead forecast |
| Output label | All predictions tagged data_type = "PREDICTED" |

## Not Implemented Yet

The ML module is NOT part of Step 1. It will be implemented in a later step
after sufficient historical data has been collected.

## Dependencies (Future)

```
pandas>=2.2.0
scikit-learn>=1.5.0
statsmodels>=0.14.2
```

These are listed (commented out) in `backend/requirements.txt` for reference.
