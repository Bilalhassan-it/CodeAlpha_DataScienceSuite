"""Forecasting: linear trend x monthly seasonal index, plus 2-sigma anomaly detection."""
import numpy as np


def forecast(series, periods):
    y = np.array([s["value"] for s in series], dtype=float)
    n = len(y)
    if n < 4:
        raise ValueError("Need at least 4 months of history")
    t = np.arange(n)
    slope, icpt = np.polyfit(t, y, 1)
    trend = slope * t + icpt

    months = [int(s["period"][5:7]) for s in series]
    ratio = y / np.where(trend == 0, 1, trend)
    idx = {m: float(np.mean([ratio[i] for i in range(n) if months[i] == m])) for m in set(months)}

    fitted = np.array([trend[i] * idx[months[i]] for i in range(n)])
    resid = y - fitted
    sigma = float(resid.std()) or 1.0
    ss_tot = float(((y - y.mean()) ** 2).sum()) or 1.0
    r2 = 1 - float((resid ** 2).sum()) / ss_tot
    mape = float(np.mean(np.abs(resid) / np.where(y == 0, 1, y)) * 100)
    rmse = float(np.sqrt((resid ** 2).mean()))

    yr, mo = int(series[-1]["period"][:4]), months[-1]
    future = []
    for k in range(1, periods + 1):
        mo += 1
        if mo > 12:
            mo, yr = 1, yr + 1
        v = (slope * (n - 1 + k) + icpt) * idx.get(mo, 1.0)
        future.append({"period": f"{yr}-{mo:02d}", "value": round(v, 2),
                       "lower": round(v - 1.96 * sigma, 2), "upper": round(v + 1.96 * sigma, 2)})

    anomalies = [{"period": series[i]["period"], "actual": round(float(y[i]), 2),
                  "expected": round(float(fitted[i]), 2), "deviation": round(float(resid[i]), 2),
                  "z": round(float(resid[i] / sigma), 2)}
                 for i in range(n) if abs(resid[i] / sigma) > 2]

    return {
        "history": [{"period": series[i]["period"], "actual": round(float(y[i]), 2),
                     "fitted": round(float(fitted[i]), 2)} for i in range(n)],
        "forecast": future,
        "metrics": {"engine": "Python · NumPy trend × seasonal", "r2": r2, "mape": mape,
                    "rmse": rmse, "slope": float(slope)},
        "anomalies": anomalies,
    }
