"""CodeAlpha Data Science Suite - interactive analytics dashboard.

Run:  streamlit run app.py
Pages: Overview, Iris classification, Unemployment analysis, Car price and Sales regression.
Every page works on a built-in sample or on your own uploaded CSV / Excel file.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import (GradientBoostingRegressor, RandomForestClassifier,
                              RandomForestRegressor)
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             mean_absolute_error, mean_squared_error, r2_score)
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# ----------------------------------------------------------------------------
# Theme
# ----------------------------------------------------------------------------
NAVY, ICE = "#0F3460", "#EEF2FF"
AMBER, TEAL, GREY = "#D98E04", "#1F9E89", "#C5D3EA"
BLUE, SKY, CORAL = "#2E6BB0", "#7FB2E5", "#E4572E"
SEQ = [[0, "#EEF2FF"], [0.5, "#7C9BD0"], [1, NAVY]]          # one hue, light -> dark
DIV = [[0, CORAL], [0.5, "#FFFFFF"], [1, BLUE]]               # two hues, neutral middle
DATA = Path(__file__).parent / "data"
LOCKDOWN = pd.Timestamp("2020-03-25")

st.set_page_config(page_title="CodeAlpha Data Science Suite", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""<style>
.stApp {{background:{ICE}; color:{NAVY};}}
.block-container {{padding-top:1.4rem; max-width:1250px;}}
[data-testid=stSidebar] {{background:{NAVY};}}
[data-testid=stSidebar] * {{color:{ICE} !important;}}
[data-testid=stSidebar] hr {{border-color:#ffffff33;}}
.stAppDeployButton, [data-testid=stDecoration] {{display:none;}}
h1,h2,h3,h4,h5,p,li,label,span,div {{color:inherit;}}
.hero {{background:linear-gradient(120deg,{NAVY} 0%,#1B4F8A 100%); padding:26px 30px;
        border-radius:16px; margin-bottom:18px;}}
.hero h1 {{color:{ICE}; margin:0; font-size:1.9rem;}}
.hero p {{color:#C9D6F5; margin:6px 0 0 0; font-size:1rem;}}
.card {{background:#fff; border-radius:14px; padding:18px 20px; box-shadow:0 1px 8px #0f34601f;
        border-top:4px solid {NAVY}; min-height:150px;}}
.card h4 {{margin:0 0 6px 0; font-size:1.05rem;}}
.card p {{margin:0; font-size:.92rem; color:#41506b;}}
.step {{background:#fff; border-radius:12px; padding:12px 14px; border-left:5px solid {AMBER};
        font-size:.92rem; box-shadow:0 1px 6px #0f34601a;}}
.insight {{background:#fff; border-left:5px solid {TEAL}; border-radius:10px; padding:10px 14px;
           margin-bottom:8px; box-shadow:0 1px 6px #0f34601a;}}
div[data-testid=stMetric] {{background:#fff; border-left:5px solid {NAVY}; padding:14px 16px;
        border-radius:12px; box-shadow:0 1px 8px #0f34601f;}}
div[data-testid=stMetricValue] {{color:{NAVY};}}
[data-testid=stMetricValue] > div {{font-size:1.65rem; white-space:normal; overflow:visible; text-overflow:clip; line-height:1.2;}}
.stTabs [data-baseweb=tab-list] {{gap:6px;}}
.stTabs [data-baseweb=tab] {{background:#fff; border-radius:10px 10px 0 0; padding:8px 18px;}}
.stTabs [aria-selected=true] {{background:{NAVY}; color:{ICE} !important;}}
.stTabs [aria-selected=true] p {{color:{ICE} !important;}}
.stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {{
        background:{NAVY}; color:{ICE}; border-radius:10px; border:0; padding:.5rem 1.2rem;}}
.stButton>button:hover, .stDownloadButton>button:hover {{background:#1B4F8A; color:#fff;}}
[data-testid=stDataFrame] {{background:#fff; border-radius:10px;}}
</style>""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Small UI helpers
# ----------------------------------------------------------------------------
def hero(title, sub):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{sub}</p></div>', unsafe_allow_html=True)


def steps(*items):
    cols = st.columns(len(items))
    for i, (c, t) in enumerate(zip(cols, items), 1):
        c.markdown(f'<div class="step"><b>Step {i}</b><br>{t}</div>', unsafe_allow_html=True)
    st.write("")


def insight(text):
    st.markdown(f'<div class="insight">{text}</div>', unsafe_allow_html=True)


def style(fig, h=380, legend=True):
    fig.update_layout(paper_bgcolor="#fff", plot_bgcolor="#fff", font=dict(color=NAVY, size=13),
                      margin=dict(t=55, l=10, r=10, b=10), height=h, showlegend=legend,
                      title=dict(font=dict(size=16), x=0.01),
                      legend=dict(orientation="h", y=-0.18, x=0))
    fig.update_xaxes(showgrid=False, linecolor="#d5dcec", zeroline=False)
    fig.update_yaxes(gridcolor="#e9edf7", zeroline=False)
    return fig


def show(fig, **kw):
    st.plotly_chart(style(fig, **kw), width="stretch")


def read_any(up):
    if up.name.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(up)
    else:
        df = pd.read_csv(up, sep=None, engine="python", encoding_errors="replace")
    df.columns = [str(c).strip() for c in df.columns]
    return df.loc[:, ~df.columns.str.startswith("Unnamed")]


def get_data(key, sample_fn, sample_name, hint):
    """Step 1 of every page: choose a sample dataset or upload your own file."""
    mode = st.radio("Where should the data come from?", ["Use the sample dataset", "Upload my own file"],
                    horizontal=True, key=key + "_mode")
    if mode == "Upload my own file":
        up = st.file_uploader("Drop a CSV or Excel file here", type=["csv", "xlsx", "xls"], key=key + "_up", help=hint)
        st.caption(hint)
        if up is None:
            st.info("No file yet. Upload one above, or switch to the sample dataset to try the tool.")
            return None, None
        try:
            return read_any(up), up.name
        except Exception as e:  # noqa: BLE001
            st.error(f"Could not read that file: {e}")
            return None, None
    return sample_fn(), sample_name


def data_health(df, name):
    miss = int(df.isna().sum().sum())
    c = st.columns(5)
    c[0].metric("Source", name if len(name) < 22 else name[:19] + "…")
    c[1].metric("Rows", f"{len(df):,}")
    c[2].metric("Columns", df.shape[1])
    c[3].metric("Missing cells", f"{miss:,}")
    c[4].metric("Duplicate rows", f"{int(df.duplicated().sum()):,}")
    with st.expander("Preview the data and column types", expanded=False):
        st.dataframe(df.head(50), width="stretch")
        info = pd.DataFrame({"Type": df.dtypes.astype(str), "Missing": df.isna().sum(),
                             "Unique values": df.nunique()})
        st.dataframe(info, width="stretch")


# ----------------------------------------------------------------------------
# Sample datasets
# ----------------------------------------------------------------------------
@st.cache_data
def sample_iris():
    d = load_iris(as_frame=True)
    df = d.frame.drop(columns="target")
    df["species"] = d.frame.target.map(dict(enumerate(d.target_names)))
    df.columns = [c.replace(" (cm)", "") for c in df.columns]
    return df


@st.cache_data
def sample_cars():
    return pd.read_csv(DATA / "car_price.csv").drop(columns="car_ID")


@st.cache_data
def sample_sales():
    return pd.read_csv(DATA / "advertising.csv").loc[:, lambda d: ~d.columns.str.startswith("Unnamed")]


@st.cache_data
def sample_unemployment():
    rng = np.random.default_rng(7)
    rows = []
    base = {"Andhra Pradesh": 6, "Assam": 5, "Bihar": 11, "Delhi": 14, "Gujarat": 5,
            "Kerala": 9, "Maharashtra": 6, "Punjab": 9, "Tamil Nadu": 8, "Uttar Pradesh": 8}
    for r, b in base.items():
        for i, d in enumerate(pd.date_range("2019-05-31", periods=17, freq="ME")):
            shock = 18 * np.exp(-((i - 11.5) ** 2) / 1.6) * rng.uniform(.5, 1.2)
            rows.append({"Region": r, "Date": d, "Estimated Unemployment Rate (%)":
                         round(max(1, b + rng.normal(0, .8) + shock), 2)})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Shared modelling utilities
# ----------------------------------------------------------------------------
def prepare(df, target):
    """Clean a table for modelling: drop IDs / free text, tidy dates, encode categories."""
    df = df.dropna(subset=[target]).copy()
    for c in list(df.columns):
        if c == target:
            continue
        col = df[c]
        if col.dtype.kind in "iu" and col.is_unique and ("id" in c.lower() or col.is_monotonic_increasing):
            df = df.drop(columns=c)                       # row id
        elif not pd.api.types.is_numeric_dtype(col) and col.nunique() > 25:
            first = col.astype(str).str.split().str[0].str.lower()
            if first.nunique() <= 30:
                df[c] = first                              # e.g. car name -> brand
                df = df.rename(columns={c: c + "_group"})
            else:
                df = df.drop(columns=c)                    # free text
    if "Year" in df.columns:
        df["Age"] = pd.Timestamp.now().year - df.pop("Year")
    num = df.select_dtypes("number").columns
    df[num] = df[num].fillna(df[num].median())
    cat = df.select_dtypes(exclude="number").columns.difference([target])
    df[cat] = df[cat].fillna("Unknown").astype(str)
    return df


def input_form(raw, key, label):
    """One widget per feature, ranges taken from the data."""
    vals, cols = {}, st.columns(3)
    for i, c in enumerate(raw.columns):
        with cols[i % 3]:
            s = raw[c]
            if s.dtype.kind in "iuf":
                lo, hi, med = float(s.min()), float(s.max()), float(s.median())
                if hi > lo:
                    vals[c] = st.slider(c, lo, hi, med, step=(hi - lo) / 100, key=f"{key}_{c}")
                else:
                    vals[c] = lo
            else:
                opts = sorted(s.astype(str).unique())
                vals[c] = st.selectbox(c, opts, index=opts.index(s.astype(str).mode()[0]), key=f"{key}_{c}")
    return vals


def encode(raw, columns=None):
    x = pd.get_dummies(raw, drop_first=False).astype(float)
    return x if columns is None else x.reindex(columns=columns, fill_value=0.0)


@st.cache_data(show_spinner="Training models…")
def train_regression(X, y, test_size):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=42)
    models = {"Linear Regression": make_pipeline(StandardScaler(), LinearRegression()),
              "Random Forest": RandomForestRegressor(300, random_state=42, n_jobs=-1),
              "Gradient Boosting": GradientBoostingRegressor(random_state=42)}
    rows, preds = [], {}
    for n, m in models.items():
        m.fit(Xtr, ytr)
        p = m.predict(Xte)
        preds[n] = p
        cv = cross_val_score(m, X, y, cv=KFold(5, shuffle=True, random_state=42), scoring="r2").mean()
        rows.append({"Model": n, "R²": r2_score(yte, p), "CV R² (5-fold)": cv,
                     "MAE": mean_absolute_error(yte, p), "RMSE": mean_squared_error(yte, p) ** .5})
    return models, pd.DataFrame(rows).set_index("Model"), preds, yte


@st.cache_data(show_spinner="Training models…")
def train_classifiers(X, y, test_size):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
    models = {"Random Forest": RandomForestClassifier(300, random_state=42, n_jobs=-1),
              "K-Nearest Neighbors": make_pipeline(StandardScaler(), KNeighborsClassifier(5)),
              "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))}
    rows, preds = [], {}
    for n, m in models.items():
        m.fit(Xtr, ytr)
        preds[n] = m.predict(Xte)
        cv = cross_val_score(m, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42)).mean()
        rows.append({"Model": n, "Accuracy": accuracy_score(yte, preds[n]), "CV accuracy (5-fold)": cv})
    return models, pd.DataFrame(rows).set_index("Model"), preds, yte


def pct(df):
    return df.style.format("{:.3f}")


# ----------------------------------------------------------------------------
# Regression page (Car price, Sales, or any numeric target)
# ----------------------------------------------------------------------------
def regression_page(title, sub, sample_fn, sample_name, default_target, key, hint, unit=""):
    hero(title, sub)
    steps("Pick sample or upload", "Explore the charts", "Train and compare models", "Predict with your values")
    raw_df, name = get_data(key, sample_fn, sample_name, hint)
    if raw_df is None:
        return
    nums = raw_df.select_dtypes("number").columns.tolist()
    if not nums:
        st.error("This file has no numeric column to predict.")
        return
    target = st.selectbox("What do you want to predict? (target column)", nums,
                          index=nums.index(default_target) if default_target in nums else len(nums) - 1,
                          key=key + "_t")
    df = prepare(raw_df, target)
    feats = [c for c in df.columns if c != target]
    if len(df) < 30 or not feats:
        st.error("Need at least 30 rows and one feature column to train a model.")
        return
    X, y = encode(df[feats]), df[target]
    data_health(raw_df, name)
    t_data, t_eda, t_model, t_pred, t_report = st.tabs(
        ["📁 Data", "📊 Explore", "🤖 Models", "🎯 Predict", "📝 Insights"])

    # ---- Data
    with t_data:
        st.markdown("**Columns used by the model** (IDs and free text are removed automatically; "
                    "long text such as a car name is reduced to its first word, e.g. the brand).")
        st.write(", ".join(f"`{c}`" for c in feats))
        st.dataframe(df.head(100), width="stretch")

    # ---- Explore
    with t_eda:
        a, b = st.columns(2)
        h = px.histogram(df, x=target, nbins=30, color_discrete_sequence=[BLUE], title=f"Distribution of {target}")
        h.update_traces(marker_line_color="#fff", marker_line_width=1)
        with a:
            show(h, legend=False)
        num_f = df[feats].select_dtypes("number").columns.tolist()
        if num_f:
            corr = df[num_f + [target]].corr()[target].drop(target).sort_values(key=abs, ascending=False)
            cb = go.Figure(go.Bar(x=corr.values[::-1], y=corr.index[::-1], orientation="h",
                                  marker_color=[TEAL if v >= 0 else CORAL for v in corr.values[::-1]]))
            cb.update_layout(title=f"What moves with {target}? (correlation)")
            with b:
                show(cb, legend=False)
            x_col = st.selectbox("Look closer: plot one feature against the target", num_f, key=key + "_x")
            sc = px.scatter(df, x=x_col, y=target, opacity=.7, color_discrete_sequence=[BLUE],
                            title=f"{target} vs {x_col}")
            if df[x_col].nunique() > 1:
                m, c0 = np.polyfit(df[x_col], df[target], 1)
                xs = np.array([df[x_col].min(), df[x_col].max()])
                sc.add_trace(go.Scatter(x=xs, y=m * xs + c0, mode="lines", name="Trend",
                                        line=dict(color=AMBER, width=3)))
            show(sc, h=400)
            if len(num_f) > 1:
                top = corr.index[:10].tolist()
                cm = df[top + [target]].corr().round(2)
                show(px.imshow(cm, text_auto=True, color_continuous_scale=DIV, zmin=-1, zmax=1,
                               title="Correlation heatmap (top related features)"), h=480)
        cats = df[feats].select_dtypes(exclude="number").columns.tolist()
        if cats:
            cc = st.selectbox("Compare the target across a category", cats, key=key + "_c")
            order = df.groupby(cc)[target].median().sort_values(ascending=False).index[:15]
            bx = px.box(df[df[cc].isin(order)], x=cc, y=target, category_orders={cc: list(order)},
                        color_discrete_sequence=[BLUE], title=f"{target} by {cc}")
            show(bx, h=420, legend=False)

    # ---- Models
    ts = st.session_state.get(key + "_ts", 0.2)
    with t_model:
        ts = st.slider("Share of data kept aside for testing", .1, .4, ts, .05, key=key + "_ts")
        models, res, preds, yte = train_regression(X, y, ts)
        best = res["CV R² (5-fold)"].idxmax()
        r = res.loc[best]
        m = st.columns(4)
        m[0].metric("Best model", best)
        m[1].metric("R² (test)", f"{r['R²']:.3f}", help="1.0 is perfect. Share of the target's variation explained.")
        m[2].metric("Typical error (MAE)", f"{r['MAE']:,.2f}")
        m[3].metric("RMSE", f"{r['RMSE']:,.2f}")
        a, b = st.columns(2)
        cmp_ = go.Figure(go.Bar(x=res.index, y=res["CV R² (5-fold)"],
                                marker_color=[BLUE if i == best else GREY for i in res.index],
                                text=res["CV R² (5-fold)"].round(3), textposition="outside"))
        cmp_.update_layout(title="Model comparison (cross-validated R², higher is better)")
        cmp_.update_yaxes(range=[min(0, res["CV R² (5-fold)"].min() - .05), 1.05])
        with a:
            show(cmp_, legend=False)
        ap = go.Figure()
        ap.add_trace(go.Scatter(x=yte, y=preds[best], mode="markers", name="Test rows",
                                marker=dict(color=BLUE, size=9, opacity=.75, line=dict(color="#fff", width=1))))
        lo, hi = float(min(yte.min(), preds[best].min())), float(max(yte.max(), preds[best].max()))
        ap.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Perfect prediction",
                                line=dict(color=AMBER, dash="dash", width=2)))
        ap.update_layout(title=f"Actual vs predicted ({best})", xaxis_title="Actual", yaxis_title="Predicted")
        with b:
            show(ap)
        a, b = st.columns(2)
        resid = yte.values - preds[best]
        rh = px.histogram(x=resid, nbins=25, color_discrete_sequence=[TEAL],
                          title="Prediction errors (centred on 0 is good)", labels={"x": "Actual − predicted"})
        rh.update_traces(marker_line_color="#fff", marker_line_width=1)
        with a:
            show(rh, legend=False)
        tree = models["Random Forest"]
        imp = pd.Series(tree.feature_importances_, index=X.columns).sort_values().tail(10)
        ib = go.Figure(go.Bar(x=imp.values, y=imp.index, orientation="h",
                              marker=dict(color=imp.values, colorscale=[[0, SKY], [1, NAVY]])))
        ib.update_layout(title="Top 10 drivers (Random Forest importance)")
        with b:
            show(ib, legend=False)
        st.markdown("**All models**")
        st.dataframe(pct(res), width="stretch")
        st.download_button("⬇ Download model comparison (CSV)", res.round(4).to_csv().encode(),
                           f"{key}_model_comparison.csv")

    # ---- Predict
    with t_pred:
        st.markdown(f"Move the sliders to describe a new case. The **{best}** model predicts **{target}**.")
        vals = input_form(df[feats], key + "_in", target)
        x_new = encode(pd.DataFrame([vals]), X.columns)
        pred = float(models[best].predict(x_new)[0])
        c = st.columns(3)
        c[0].metric(f"Predicted {target}", f"{pred:,.2f} {unit}".strip())
        c[1].metric("Likely range", f"{pred - r['RMSE']:,.0f} to {pred + r['RMSE']:,.0f}",
                    help="Prediction ± the model's typical error (RMSE).")
        c[2].metric("Dataset average", f"{y.mean():,.2f}")

    # ---- Insights
    with t_report:
        top3 = imp.index[::-1][:3].tolist()
        rel = r["MAE"] / max(abs(y.mean()), 1e-9)
        quality = "excellent" if r["R²"] > .9 else "strong" if r["R²"] > .75 else "moderate" if r["R²"] > .5 else "weak"
        lines = [f"<b>{best}</b> is the best model: it explains <b>{r['R²']:.0%}</b> of the variation in {target} ({quality} fit).",
                 f"The typical prediction is off by about <b>{r['MAE']:,.2f}</b> ({rel:.0%} of the average {target}).",
                 f"The strongest drivers are <b>{', '.join(top3)}</b>.",
                 f"The data has <b>{len(df):,}</b> usable rows and <b>{len(feats)}</b> input columns."]
        if num_f:
            best_c = corr.index[0]
            lines.append(f"<b>{best_c}</b> has the strongest straight-line link with {target} (correlation {corr.iloc[0]:+.2f}).")
        for t in lines:
            insight(t)
        report = (f"# {title}\n\nData: {name} ({len(df)} rows)\n\nTarget: {target}\n\nBest model: {best}\n\n"
                  + "\n".join("- " + l.replace("<b>", "**").replace("</b>", "**") for l in lines)
                  + "\n\n## Model comparison\n\n" + "```\n" + res.round(4).to_string() + "\n```")
        st.download_button("⬇ Download report (Markdown)", report.encode(), f"{key}_report.md")


# ----------------------------------------------------------------------------
# Classification page (Iris or any labelled table)
# ----------------------------------------------------------------------------
def classification_page():
    hero("Iris Flower Classification", "Task 1 · Teach a model to recognise a category from measurements. "
         "Works with the Iris sample or any CSV that has a label column.")
    steps("Pick sample or upload", "Explore the classes", "Train and compare models", "Classify a new case")
    raw_df, name = get_data("iris", sample_iris, "Iris sample",
                            "Upload a table with numeric measurements and one label column, such as species or class.")
    if raw_df is None:
        return
    cand = [c for c in raw_df.columns if not pd.api.types.is_numeric_dtype(raw_df[c]) or raw_df[c].nunique() <= 10]
    if not cand:
        st.error("No label column found. A label column has text values or only a few distinct values.")
        return
    target = st.selectbox("Which column is the label to predict?", cand,
                          index=cand.index("species") if "species" in cand else 0, key="iris_t")
    df = raw_df.dropna(subset=[target]).copy()
    df[target] = df[target].astype(str)
    df = prepare(df, target)
    feats = [c for c in df.columns if c != target]
    if len(df) < 30 or df[target].value_counts().min() < 5 or not feats:
        st.error("Need at least 30 rows, and at least 5 rows for every label value.")
        return
    X, y = encode(df[feats]), df[target]
    data_health(raw_df, name)
    t_data, t_eda, t_model, t_pred = st.tabs(["📁 Data", "📊 Explore", "🤖 Models", "🎯 Classify"])

    with t_data:
        counts = y.value_counts().reset_index()
        counts.columns = [target, "rows"]
        cb = px.bar(counts, x=target, y="rows", color_discrete_sequence=[BLUE], text="rows",
                    title="How many rows per class (balanced is easier)")
        show(cb, h=300, legend=False)
        st.dataframe(df.head(100), width="stretch")

    num_f = df[feats].select_dtypes("number").columns.tolist()
    with t_eda:
        if len(num_f) >= 2:
            a, b = st.columns(2)
            x1 = a.selectbox("X axis", num_f, index=0, key="iris_x")
            y1 = b.selectbox("Y axis", num_f, index=1, key="iris_y")
            pal = [BLUE, AMBER, TEAL, CORAL, "#6C5B7B", "#8D99AE"]
            sc = px.scatter(df, x=x1, y=y1, color=target, color_discrete_sequence=pal,
                            title=f"{y1} vs {x1}")
            sc.update_traces(marker=dict(size=10, line=dict(color="#fff", width=1.5)))
            show(sc, h=430)
        if num_f:
            f1 = st.selectbox("Compare one measurement across classes", num_f, key="iris_box")
            show(px.box(df, x=target, y=f1, color=target, color_discrete_sequence=[BLUE, AMBER, TEAL, CORAL],
                        title=f"{f1} by class"), h=380, legend=False)
            cm = df[num_f].corr().round(2)
            show(px.imshow(cm, text_auto=True, color_continuous_scale=DIV, zmin=-1, zmax=1,
                           title="How the measurements relate to each other"), h=420)

    with t_model:
        ts = st.slider("Share of data kept aside for testing", .1, .4, .2, .05, key="iris_ts")
        models, res, preds, yte = train_classifiers(X, y, ts)
        best = res["CV accuracy (5-fold)"].idxmax()
        choice = st.selectbox("Show details for", list(models), index=list(models).index(best), key="iris_m")
        p = preds[choice]
        m = st.columns(4)
        m[0].metric("Model", choice)
        m[1].metric("Test accuracy", f"{accuracy_score(yte, p):.1%}")
        m[2].metric("Cross-validated accuracy", f"{res.loc[choice, 'CV accuracy (5-fold)']:.1%}",
                    help="Average over 5 different splits: a more honest estimate than one test split.")
        m[3].metric("Train / test rows", f"{len(X) - len(yte)} / {len(yte)}")
        a, b = st.columns(2)
        labels = sorted(y.unique())
        cmx = confusion_matrix(yte, p, labels=labels)
        with a:
            show(px.imshow(cmx, x=labels, y=labels, text_auto=True, color_continuous_scale=SEQ,
                           labels=dict(x="Predicted", y="Actual", color="Rows"), title="Confusion matrix"), h=380)
        cmp_ = go.Figure(go.Bar(x=res.index, y=res["CV accuracy (5-fold)"],
                                marker_color=[BLUE if i == choice else GREY for i in res.index],
                                text=(res["CV accuracy (5-fold)"] * 100).round(1).astype(str) + "%",
                                textposition="outside"))
        cmp_.update_layout(title="Model comparison (cross-validated accuracy)")
        cmp_.update_yaxes(range=[0, 1.1], tickformat=".0%")
        with b:
            show(cmp_, h=380, legend=False)
        rep = pd.DataFrame(classification_report(yte, p, output_dict=True)).T.round(2)
        st.markdown("**Per-class report** (precision: how often a prediction is right; recall: how many real cases were found)")
        st.dataframe(rep, width="stretch")
        if choice == "Random Forest":
            imp = pd.Series(models[choice].feature_importances_, index=X.columns).sort_values().tail(10)
            ib = go.Figure(go.Bar(x=imp.values, y=imp.index, orientation="h",
                              marker=dict(color=imp.values, colorscale=[[0, SKY], [1, NAVY]])))
            ib.update_layout(title="Which measurements matter most")
            show(ib, h=340, legend=False)
        st.download_button("⬇ Download model comparison (CSV)", res.round(4).to_csv().encode(),
                           "classification_comparison.csv")

    with t_pred:
        st.markdown(f"Describe a new case. The **{choice}** model will pick its class.")
        vals = input_form(df[feats], "iris_in", target)
        x_new = encode(pd.DataFrame([vals]), X.columns)
        mdl = models[choice]
        label = mdl.predict(x_new)[0]
        c = st.columns([1, 2])
        c[0].metric("Predicted class", str(label))
        if hasattr(mdl, "predict_proba"):
            pr = pd.Series(mdl.predict_proba(x_new)[0], index=mdl.classes_)
            pb = go.Figure(go.Bar(x=pr.values, y=pr.index, orientation="h",
                                  marker_color=[BLUE if i == label else GREY for i in pr.index],
                                  text=(pr * 100).round(1).astype(str) + "%", textposition="outside"))
            pb.update_layout(title="Confidence per class")
            pb.update_xaxes(range=[0, 1.15], tickformat=".0%")
            with c[1]:
                show(pb, h=260, legend=False)


# ----------------------------------------------------------------------------
# Unemployment page
# ----------------------------------------------------------------------------
def guess(cols, *keys, avoid=()):
    for k in keys:
        for c in cols:
            if all(w in c.lower() for w in k) and not any(a in c.lower() for a in avoid):
                return c
    return None


def unemployment_page():
    hero("Unemployment Analysis", "Task 2 · See how the unemployment rate moved over time, which regions were hit "
         "hardest, and what changed after the Covid-19 lockdown.")
    steps("Pick sample or upload", "Check column mapping", "Explore trends and regions", "Read the insights")
    raw, name = get_data("unemp", sample_unemployment, "Synthetic sample",
                         "Needs a date column and a numeric unemployment-rate column. A region/state column is optional.")
    if raw is None:
        return
    cols = list(raw.columns)
    with st.expander("Column mapping (detected automatically, change it if needed)", expanded=False):
        c = st.columns(3)
        dflt_d = guess(cols, ("date",), ("month",), ("time",)) or cols[0]
        dflt_r = guess(cols, ("unemployment", "rate"), ("rate",), ("unemployment",)) or cols[-1]
        dflt_g = guess(cols, ("region",), ("state",), ("area",), ("country",))
        dc = c[0].selectbox("Date column", cols, index=cols.index(dflt_d))
        rc = c[1].selectbox("Unemployment rate column", cols, index=cols.index(dflt_r))
        opts = ["(none)"] + cols
        gc = c[2].selectbox("Region / state column", opts, index=opts.index(dflt_g) if dflt_g else 0)
    df = raw.copy()
    ds = df[dc].astype(str).str.strip()
    df[dc] = (pd.to_datetime(ds, errors="coerce") if ds.str.match(r"^\d{4}-").all()
              else pd.to_datetime(ds, dayfirst=True, errors="coerce"))
    df[rc] = pd.to_numeric(df[rc], errors="coerce")
    df = df.dropna(subset=[dc, rc]).sort_values(dc)
    if df.empty:
        st.error("After reading the date and rate columns no rows were left. Check the column mapping above.")
        return
    region = None if gc == "(none)" else gc
    if region is None:
        df["Region"], region = "All", "Region"
    data_health(raw, name)

    f1, f2, f3 = st.columns([2, 2, 2])
    all_r = sorted(df[region].astype(str).unique())
    sel = f1.multiselect("Regions to include", all_r, default=all_r[:8] if len(all_r) > 8 else all_r)
    d0, d1 = df[dc].min().to_pydatetime(), df[dc].max().to_pydatetime()
    rng = f2.slider("Period", d0, d1, (d0, d1), format="MMM YYYY") if d0 < d1 else (d0, d1)
    ev = f3.date_input("Compare before / after this date", LOCKDOWN.date(),
                       help="Default is the national lockdown in India, 25 March 2020.")
    df[region] = df[region].astype(str)
    df = df[df[region].isin(sel) & df[dc].between(pd.Timestamp(rng[0]), pd.Timestamp(rng[1]))]
    if df.empty:
        st.warning("Nothing to show for this selection. Choose at least one region and a wider period.")
        return
    ev = pd.Timestamp(ev)
    df["Period"] = np.where(df[dc] < ev, "Before", "After")
    pre, post = df[df.Period == "Before"][rc].mean(), df[df.Period == "After"][rc].mean()
    pk = df.loc[df[rc].idxmax()]
    reg_avg = df.groupby(region)[rc].mean().sort_values(ascending=False)
    t1, t2, t3, t4, t5 = st.tabs(["🏠 Summary", "📈 Trends", "🗺 Regions", "🦠 Before vs after", "📝 Insights"])

    with t1:
        m = st.columns(4)
        m[0].metric("Average rate", f"{df[rc].mean():.1f}%")
        m[1].metric("Before the date", f"{pre:.1f}%" if pd.notna(pre) else "n/a")
        m[2].metric("After the date", f"{post:.1f}%" if pd.notna(post) else "n/a",
                    f"{post - pre:+.1f} pts" if pd.notna(pre) and pd.notna(post) else None, delta_color="inverse")
        m[3].metric("Peak", f"{pk[rc]:.1f}%", f"{pk[region]}, {pk[dc]:%b %Y}", delta_color="off")
        nat = df.groupby(dc)[rc].mean().reset_index()
        nat["3-month average"] = nat[rc].rolling(3, min_periods=1).mean()
        fg = go.Figure()
        fg.add_trace(go.Scatter(x=nat[dc], y=nat[rc], name="Monthly average", mode="lines",
                                line=dict(color=GREY, width=2)))
        fg.add_trace(go.Scatter(x=nat[dc], y=nat["3-month average"], name="3-month average", mode="lines",
                                line=dict(color=BLUE, width=4), fill="tozeroy", fillcolor="rgba(46,107,176,.10)"))
        if nat[dc].min() < ev < nat[dc].max():
            fg.add_vline(x=ev.timestamp() * 1000, line_dash="dash", line_color=AMBER)
            fg.add_annotation(x=ev, y=1, yref="paper", text="Event date", showarrow=False,
                              font=dict(color=AMBER), xanchor="left")
        fg.update_layout(title="Average unemployment rate across selected regions", yaxis_title="Rate (%)")
        show(fg, h=400)

    with t2:
        focus = st.selectbox("Highlight one region", sel, index=sel.index(reg_avg.index[0]) if reg_avg.index[0] in sel else 0)
        fg = go.Figure()
        for r_, g in df.groupby(region):
            fg.add_trace(go.Scatter(x=g[dc], y=g[rc], mode="lines", name=r_, showlegend=(r_ == focus),
                                    line=dict(color=CORAL if r_ == focus else "#C9D6EE", width=4.5 if r_ == focus else 1.6),
                                    hovertemplate=f"{r_}<br>%{{x|%b %Y}}: %{{y:.1f}}%<extra></extra>"))
        fg.update_layout(title=f"{focus} (highlighted) against every other region (light)", yaxis_title="Rate (%)")
        show(fg, h=420)
        a, b = st.columns(2)
        mo = df.assign(Month=df[dc].dt.month).groupby("Month")[rc].mean().reset_index()
        mo["Name"] = pd.to_datetime(mo.Month, format="%m").dt.strftime("%b")
        mb = px.bar(mo, x="Name", y=rc, color_discrete_sequence=[BLUE], title="Seasonality: average rate by calendar month")
        mb.update_layout(yaxis_title="Rate (%)", xaxis_title="")
        with a:
            show(mb, legend=False)
        hm = df.assign(Month=df[dc].dt.to_period("M").astype(str)).pivot_table(index=region, columns="Month", values=rc)
        with b:
            show(px.imshow(hm, color_continuous_scale=SEQ, aspect="auto",
                           labels=dict(color="Rate %"), title="Heatmap: darker is higher unemployment"))

    with t3:
        a, b = st.columns(2)
        rb = go.Figure(go.Bar(x=reg_avg.values[::-1], y=reg_avg.index[::-1], orientation="h",
                              marker_color=[CORAL if i == 0 else BLUE for i in range(len(reg_avg))][::-1],
                              text=reg_avg.round(1).values[::-1], textposition="outside"))
        rb.update_layout(title="Average rate by region (highest in coral)")
        with a:
            show(rb, h=max(340, 34 * len(reg_avg) + 90), legend=False)
        vol = df.groupby(region)[rc].std().sort_values(ascending=False).dropna()
        vb = go.Figure(go.Bar(x=vol.values[::-1], y=vol.index[::-1], orientation="h", marker_color=SKY,
                              text=vol.round(1).values[::-1], textposition="outside"))
        vb.update_layout(title="How unstable the rate was (standard deviation)")
        with b:
            show(vb, h=max(340, 34 * len(vol) + 90), legend=False)
        show(px.box(df, x=region, y=rc, color_discrete_sequence=[BLUE], title="Spread of the rate per region"),
             h=420, legend=False)

    with t4:
        ba = df.groupby([region, "Period"])[rc].mean().unstack()
        if {"Before", "After"} <= set(ba.columns):
            ba = ba.dropna().sort_values("After", ascending=False)
            gb = go.Figure()
            gb.add_trace(go.Bar(x=ba.index, y=ba["Before"], name="Before", marker_color=SKY))
            gb.add_trace(go.Bar(x=ba.index, y=ba["After"], name="After", marker_color=NAVY))
            gb.update_layout(barmode="group", title="Average rate before vs after the chosen date", yaxis_title="Rate (%)")
            show(gb, h=420)
            chg = (ba["After"] - ba["Before"]).sort_values()
            cb = go.Figure(go.Bar(x=chg.values, y=chg.index, orientation="h",
                                  marker_color=[TEAL if v < 0 else CORAL for v in chg.values],
                                  text=[f"{v:+.1f}" for v in chg.values], textposition="outside"))
            cb.update_layout(title="Change in percentage points (coral = worse, teal = better)")
            show(cb, h=max(340, 34 * len(chg) + 90), legend=False)
        else:
            st.info("The selected period only has data on one side of the chosen date. Widen the period "
                    "or change the date to see a before / after comparison.")

    with t5:
        worst = reg_avg.index[0]
        notes = [f"Across the selected data the average unemployment rate is <b>{df[rc].mean():.1f}%</b>.",
                 f"The highest single value is <b>{pk[rc]:.1f}%</b> in <b>{pk[region]}</b> ({pk[dc]:%B %Y}).",
                 f"<b>{worst}</b> has the highest average rate (<b>{reg_avg.iloc[0]:.1f}%</b>); "
                 f"<b>{reg_avg.index[-1]}</b> has the lowest (<b>{reg_avg.iloc[-1]:.1f}%</b>)."]
        if pd.notna(pre) and pd.notna(post):
            notes.append(f"Compared with before {ev:%d %b %Y}, the average moved from <b>{pre:.1f}%</b> to <b>{post:.1f}%</b> "
                         f"(<b>{post - pre:+.1f}</b> percentage points).")
        if len(mo) > 1:
            notes.append(f"Seasonally the highest month on average is <b>{mo.loc[mo[rc].idxmax(), 'Name']}</b> "
                         f"and the lowest is <b>{mo.loc[mo[rc].idxmin(), 'Name']}</b>.")
        notes.append("Policy angle: regions with the highest average and the sharpest jump need targeted relief, "
                     "job-creation programmes and re-skilling.")
        for t in notes:
            insight(t)
        txt = "# Unemployment analysis\n\n" + "\n".join("- " + n.replace("<b>", "**").replace("</b>", "**") for n in notes)
        st.download_button("⬇ Download report (Markdown)", txt.encode(), "unemployment_report.md")
        st.download_button("⬇ Download filtered data (CSV)", df.drop(columns="Period").to_csv(index=False).encode(),
                           "unemployment_filtered.csv")


# ----------------------------------------------------------------------------
# Overview + navigation
# ----------------------------------------------------------------------------
PAGES = ["🏠 Overview", "🌸 Task 1 · Iris", "📉 Task 2 · Unemployment", "🚗 Task 3 · Car Price", "📺 Task 4 · Sales"]


def go_to(p):
    st.session_state["_goto"] = p


def overview():
    hero("Data Science Analytics Suite", "CodeAlpha Data Science Internship · four projects in one easy dashboard. "
         "No code needed: pick a page, choose a dataset, read the results.")
    cards = [("🌸 Iris classification", "Predict a flower species from its measurements. Works with any labelled table.", PAGES[1]),
             ("📉 Unemployment analysis", "Trends, regions, seasonality and the before / after effect of Covid-19.", PAGES[2]),
             ("🚗 Car price prediction", "Predict a car's selling price and see which features drive it.", PAGES[3]),
             ("📺 Sales prediction", "See how TV, radio and newspaper advertising turn into sales.", PAGES[4])]
    cols = st.columns(4)
    for c, (t, d, p) in zip(cols, cards):
        c.markdown(f'<div class="card"><h4>{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
        if c.button("Open", key="open_" + p, width="stretch"):
            go_to(p)
            st.rerun()
    st.write("")
    st.subheader("How to use it")
    steps("Open a page from the left menu", "Choose the sample data or upload your CSV / Excel file",
          "Read the charts and model results", "Type new values to get a prediction")
    a, b = st.columns(2)
    with a:
        st.subheader("What the pages give you")
        for t in ["Data health check: rows, missing values, duplicates, column types",
                  "Clear charts: distributions, trends, heatmaps, comparisons",
                  "Three models compared fairly with cross-validation",
                  "Plain-language insights and a report you can download"]:
            insight(t)
    with b:
        st.subheader("Files you can upload")
        st.dataframe(pd.DataFrame({
            "Page": ["Iris", "Unemployment", "Car price", "Sales"],
            "What the file needs": ["Numeric columns + one label column", "A date column + a rate column (+ region)",
                                    "Numeric / category columns + a price column", "Numeric columns + a sales column"]}),
            hide_index=True, width="stretch")
        st.caption("Sample data: Iris (scikit-learn), car prices and advertising sales (public datasets in the data/ folder), "
                   "and a clearly labelled synthetic unemployment sample.")


# Jump requested by an "Open" button: apply it before the menu widget is created.
if "_goto" in st.session_state:
    st.session_state["nav"] = st.session_state.pop("_goto")
st.sidebar.markdown("## 📊 CodeAlpha\n**Data Science Suite**")
st.sidebar.divider()
page = st.sidebar.radio("Go to", PAGES, key="nav", label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Intern: Syed Muhammad Bilal Hassan")

if page == PAGES[0]:
    overview()
elif page == PAGES[1]:
    classification_page()
elif page == PAGES[2]:
    unemployment_page()
elif page == PAGES[3]:
    regression_page("Car Price Prediction", "Task 3 · Predict a car's selling price and learn what drives it.",
                    sample_cars, "Car price sample", "price", "car",
                    "Upload a car table with a numeric price column (and features such as engine size, weight, brand).")
else:
    regression_page("Sales Prediction", "Task 4 · See how advertising spend turns into sales.",
                    sample_sales, "Advertising sample", "Sales", "sales",
                    "Upload a table with advertising spend columns (TV, Radio, Newspaper...) and a sales column.")
