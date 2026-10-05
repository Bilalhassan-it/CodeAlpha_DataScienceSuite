"""CodeAlpha Data Science Internship - Analytics Suite (Tasks 1-4). Run: streamlit run app.py"""
import numpy as np, pandas as pd, plotly.express as px, streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             mean_absolute_error, mean_squared_error, r2_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

NAVY, ICE = "#0F3460", "#EEF2FF"
PAL = [NAVY, "#3B6FB6", "#8FB0E0", "#C7D6F2"]
st.set_page_config(page_title="CodeAlpha Data Science Suite", page_icon="📊", layout="wide")
st.markdown(f"""<style>
.stApp{{background:{ICE};color:{NAVY}}}
[data-testid=stSidebar]{{background:{NAVY}}}
[data-testid=stSidebar] *{{color:{ICE}!important}}
h1,h2,h3,h4,label,p,li{{color:{NAVY}}}
div[data-testid=stMetric]{{background:#fff;border-left:5px solid {NAVY};padding:14px;border-radius:10px;box-shadow:0 1px 6px #0f34602b}}
.stButton>button,.stFormSubmitButton>button{{background:{NAVY};color:{ICE};border-radius:8px;border:0}}
</style>""", unsafe_allow_html=True)

def style(f):
    f.update_layout(paper_bgcolor="#fff", plot_bgcolor="#fff", font_color=NAVY,
                    margin=dict(t=50, l=10, r=10, b=10), colorway=PAL)
    return f

def load(key, demo):
    up = st.file_uploader("Upload the official CodeAlpha CSV (optional)", type="csv", key=key)
    if up:
        return pd.read_csv(up)
    st.info("Showing built-in **demo data (synthetic)**. Upload the official dataset for your submission.")
    return demo()

rng = np.random.default_rng(42)

@st.cache_data
def demo_unemp():
    rows = []
    for r, b in zip(["Delhi", "Kerala", "Punjab", "Bihar", "Assam"], [16, 9, 8, 11, 5]):
        for i, d in enumerate(pd.date_range("2019-01-01", periods=22, freq="MS")):
            shock = 20 * np.exp(-((i - 15) ** 2) / 3) * rng.uniform(.6, 1.2)
            rows.append({"Region": r, "Date": d, "Estimated Unemployment Rate (%)": max(1, b + rng.normal(0, 1) + shock)})
    return pd.DataFrame(rows)

@st.cache_data
def demo_cars():
    n = 300
    df = pd.DataFrame({"Year": rng.integers(2005, 2021, n), "Present_Price": rng.uniform(2, 30, n).round(2),
                       "Driven_kms": rng.integers(5000, 150000, n), "Fuel_Type": rng.choice(["Petrol", "Diesel", "CNG"], n),
                       "Transmission": rng.choice(["Manual", "Automatic"], n), "Owner": rng.integers(0, 3, n)})
    df["Selling_Price"] = (df.Present_Price * (0.9 - 0.045 * (2021 - df.Year)) - df.Driven_kms / 4e5
                           + rng.normal(0, .5, n)).clip(lower=.2).round(2)
    return df

@st.cache_data
def demo_sales():
    n = 200
    df = pd.DataFrame({"TV": rng.uniform(10, 300, n), "Radio": rng.uniform(0, 50, n), "Newspaper": rng.uniform(0, 100, n)})
    df["Sales"] = 3 + .045 * df.TV + .19 * df.Radio + .002 * df.Newspaper + rng.normal(0, 1, n)
    return df.round(2)

# ---------------- Task 1: Iris ----------------
def iris_page():
    st.title("Iris Flower Classification"); st.caption("Task 1 · Multi-class classification with scikit-learn")
    d = load_iris(as_frame=True); df = d.frame
    df["species"] = df.target.map(dict(enumerate(d.target_names))); X, y = df[d.feature_names], df.species
    c1, c2 = st.columns(2)
    algo = c1.selectbox("Algorithm", ["Random Forest", "K-Nearest Neighbors", "Logistic Regression"])
    ts = c2.slider("Test size", .1, .4, .2, .05)
    mdl = {"Random Forest": RandomForestClassifier(200, random_state=42),
           "K-Nearest Neighbors": make_pipeline(StandardScaler(), KNeighborsClassifier(5)),
           "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))}[algo]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=ts, random_state=42, stratify=y)
    mdl.fit(Xtr, ytr); p = mdl.predict(Xte)
    m = st.columns(3)
    m[0].metric("Test accuracy", f"{accuracy_score(yte, p):.1%}")
    m[1].metric("Train / test rows", f"{len(Xtr)} / {len(Xte)}")
    m[2].metric("5-fold CV accuracy", f"{cross_val_score(mdl, X, y, cv=5).mean():.1%}")
    labels = sorted(y.unique()); a, b = st.columns(2)
    a.plotly_chart(style(px.imshow(confusion_matrix(yte, p, labels=labels), x=labels, y=labels, text_auto=True,
                   color_continuous_scale=[ICE, NAVY], labels=dict(x="Predicted", y="Actual"), title="Confusion matrix")), use_container_width=True)
    b.subheader("Classification report")
    b.dataframe(pd.DataFrame(classification_report(yte, p, output_dict=True)).T.round(2), use_container_width=True)
    st.plotly_chart(style(px.scatter_matrix(df, dimensions=d.feature_names, color="species", title="Feature relationships")), use_container_width=True)
    st.subheader("Live species predictor")
    cols = st.columns(4); v = [cols[i].slider(f, float(X[f].min()), float(X[f].max()), float(X[f].median())) for i, f in enumerate(d.feature_names)]
    st.success(f"Predicted species: **{mdl.predict(pd.DataFrame([v], columns=d.feature_names))[0]}**")

# ---------------- Task 2: Unemployment ----------------
def unemployment_page():
    st.title("Unemployment Analysis"); st.caption("Task 2 · Trends, seasonality and Covid-19 impact")
    df = load("unemp", demo_unemp); df.columns = df.columns.str.strip()
    find = lambda *k: next((c for c in df.columns if all(x in c.lower() for x in k)), None)
    dc, rc, gc = find("date"), find("unemployment", "rate"), find("region") or find("state")
    if not (dc and rc):
        st.error("CSV needs a date column and an 'Unemployment Rate' column."); return
    df[dc] = pd.to_datetime(df[dc].astype(str).str.strip(), dayfirst=True, errors="coerce")
    df = df.dropna(subset=[dc, rc]).sort_values(dc)
    if gc:
        sel = st.multiselect("Regions", sorted(df[gc].unique()), default=sorted(df[gc].unique())[:6]); df = df[df[gc].isin(sel)]
    cut = pd.Timestamp("2020-03-25"); pre, post = df[df[dc] < cut][rc].mean(), df[df[dc] >= cut][rc].mean()
    pk = df.loc[df[rc].idxmax()]
    m = st.columns(4)
    m[0].metric("Average rate", f"{df[rc].mean():.1f}%"); m[1].metric("Pre-Covid average", f"{pre:.1f}%")
    m[2].metric("During/after Covid", f"{post:.1f}%", f"{post - pre:+.1f} pts", delta_color="inverse")
    m[3].metric("Peak", f"{pk[rc]:.1f}%", pk[dc].strftime("%b %Y"), delta_color="off")
    f = px.line(df, x=dc, y=rc, color=gc, title="Unemployment rate over time (dashed line = national lockdown, 25 Mar 2020)")
    f.add_vline(x=cut.timestamp() * 1000, line_dash="dash", line_color=NAVY)
    st.plotly_chart(style(f), use_container_width=True)
    a, b = st.columns(2)
    df["Period"] = np.where(df[dc] < cut, "Pre-Covid", "Covid era")
    if gc:
        a.plotly_chart(style(px.bar(df.groupby([gc, "Period"])[rc].mean().reset_index(), x=gc, y=rc, color="Period", barmode="group",
                       title="Average rate by region")), use_container_width=True)
    seas = df.assign(Month=df[dc].dt.month_name().str[:3]).groupby("Month")[rc].mean().reindex(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]).dropna().reset_index()
    b.plotly_chart(style(px.bar(seas, x="Month", y=rc, title="Seasonal pattern (average by month)")), use_container_width=True)
    st.subheader("Key insights")
    st.markdown(f"- Unemployment averaged **{pre:.1f}%** before lockdown and **{post:.1f}%** afterwards ({post - pre:+.1f} points).\n"
                f"- The peak of **{pk[rc]:.1f}%** occurred in **{pk[dc].strftime('%B %Y')}**.\n"
                f"- Policy angle: regions with the sharpest spike need targeted relief and re-skilling programmes.")

# ---------------- Tasks 3 & 4: regression ----------------
def regression_page(title, sub, df, default, key):
    st.title(title); st.caption(sub)
    df = df.copy(); df.columns = df.columns.str.strip(); df = df.dropna()
    if "Year" in df:
        df["Car_Age"] = pd.Timestamp.now().year - df.pop("Year")
    num = df.select_dtypes("number").columns.tolist()
    t = st.selectbox("Target to predict", num, index=num.index(default) if default in num else len(num) - 1, key=key + "t")
    junk = [c for c in df.select_dtypes(exclude="number") if df[c].nunique() > 15]
    raw, y = df.drop(columns=[t] + junk), df[t]
    X = pd.get_dummies(raw, drop_first=True).astype(float)
    ts = st.slider("Test size", .1, .4, .2, .05, key=key + "s")
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=ts, random_state=42)
    models = {"Linear Regression": make_pipeline(StandardScaler(), LinearRegression()),
              "Random Forest": RandomForestRegressor(300, random_state=42)}
    res, pred = [], {}
    for n, mo in models.items():
        mo.fit(Xtr, ytr); pred[n] = mo.predict(Xte)
        res.append({"Model": n, "R²": r2_score(yte, pred[n]), "MAE": mean_absolute_error(yte, pred[n]),
                    "RMSE": mean_squared_error(yte, pred[n]) ** .5})
    res = pd.DataFrame(res).set_index("Model"); best = res["R²"].idxmax(); r = res.loc[best]
    m = st.columns(4)
    m[0].metric("Best model", best); m[1].metric("R²", f"{r['R²']:.3f}"); m[2].metric("MAE", f"{r['MAE']:.2f}"); m[3].metric("RMSE", f"{r['RMSE']:.2f}")
    a, b = st.columns(2)
    f = px.scatter(x=yte, y=pred[best], labels=dict(x="Actual", y="Predicted"), title=f"Actual vs predicted ({best})")
    f.add_shape(type="line", x0=yte.min(), y0=yte.min(), x1=yte.max(), y1=yte.max(), line=dict(color=NAVY, dash="dash"))
    a.plotly_chart(style(f), use_container_width=True)
    imp = pd.Series(models["Random Forest"].feature_importances_, index=X.columns).sort_values().tail(10)
    b.plotly_chart(style(px.bar(imp, orientation="h", title="Top drivers (Random Forest importance)", labels=dict(value="Importance", index=""))), use_container_width=True)
    coef = pd.Series(models["Linear Regression"][-1].coef_ / Xtr.std().values, index=X.columns).round(4)
    with st.expander("Impact per unit change (linear model coefficients)"):
        st.dataframe(coef.rename("Change in target per +1 unit"), use_container_width=True)
    st.subheader("Live prediction")
    with st.form(key + "f"):
        vals, cols = {}, st.columns(3)
        for i, c in enumerate(raw.columns):
            with cols[i % 3]:
                vals[c] = (st.number_input(c, value=float(raw[c].median())) if raw[c].dtype.kind in "iuf"
                           else st.selectbox(c, sorted(raw[c].astype(str).unique())))
        go = st.form_submit_button("Predict")
    if go:
        x = pd.get_dummies(pd.DataFrame([vals])).reindex(columns=X.columns, fill_value=0).astype(float)
        st.metric(f"Predicted {t}", f"{models[best].predict(x)[0]:,.2f}")
    st.download_button("Download model comparison (CSV)", res.round(4).to_csv().encode(), f"{key}_metrics.csv")

# ---------------- Navigation ----------------
pages = ["Overview", "Task 1 · Iris", "Task 2 · Unemployment", "Task 3 · Car Price", "Task 4 · Sales"]
st.sidebar.markdown("## 📊 CodeAlpha\n**Data Science Internship**")
page = st.sidebar.radio("Navigate", pages, label_visibility="collapsed")
if page == pages[0]:
    st.title("Data Science Analytics Suite"); st.caption("CodeAlpha internship · four projects, one dashboard")
    c = st.columns(4)
    for col, (h, t) in zip(c, [("Iris", "Classification"), ("Unemployment", "EDA & Covid impact"), ("Car Price", "Regression"), ("Sales", "Forecasting")]):
        col.metric(h, t)
    st.markdown("### Submission checklist\n1. Push this folder to GitHub as `CodeAlpha_DataScienceSuite`\n"
                "2. Post a LinkedIn video demo tagging @CodeAlpha with the repo link\n3. Submit via the WhatsApp-group form\n\n"
                "Complete at least 2 to 3 tasks to qualify for the certificate.")
elif page == pages[1]: iris_page()
elif page == pages[2]: unemployment_page()
elif page == pages[3]: regression_page("Car Price Prediction", "Task 3 · Regression with feature engineering", load("car", demo_cars), "Selling_Price", "car")
else: regression_page("Sales Prediction", "Task 4 · Advertising impact on sales", load("sales", demo_sales), "Sales", "sales")
