<h1 align="center">CodeAlpha Data Science Suite</h1>
<p align="center"><b>CodeAlpha Data Science Internship · October 2026</b></p>
<p align="center">
<img src="https://img.shields.io/badge/CodeAlpha-Data%20Science%20Intern-0F3460" alt="CodeAlpha">
<img src="https://img.shields.io/badge/Python-3.10%2B-0F3460" alt="Python">
<img src="https://img.shields.io/badge/Streamlit-Dashboard-0F3460" alt="Streamlit">
<img src="https://img.shields.io/badge/License-MIT-0F3460" alt="MIT">
</p>

An interactive analytics dashboard that brings four data science projects together in one professional web app. It was built for the **CodeAlpha Data Science Internship** (October 2026) using Python and Streamlit.

> Navy `#0F3460` and ice `#EEF2FF` theme · Python · pandas · scikit-learn · Plotly · Streamlit

---

## 1. About the Project

Instead of four separate notebooks, this project turns each internship task into a working tool. You can pick a model, change settings, upload your own data, see the results as charts and metrics, and make live predictions, all from the browser with no code changes.

| Task | Project | Problem type | What it does |
|------|---------|--------------|--------------|
| 1 | **Iris Flower Classification** | Classification | Predicts the species (setosa, versicolor, virginica) from flower measurements |
| 2 | **Unemployment Analysis** | EDA and trend analysis | Explores unemployment trends, seasonality and the impact of Covid-19 |
| 3 | **Car Price Prediction** | Regression | Predicts a car's selling price from its features |
| 4 | **Sales Prediction** | Regression | Predicts sales from advertising spend and shows which channel matters most |

---

## 2. Benefits

- **Everything in one place.** Four projects, one dashboard, one link to share.
- **No coding needed to use it.** Sliders, dropdowns and upload buttons replace editing code.
- **Real, working models.** Models are trained and evaluated on the fly, with train/test splits and cross-validation.
- **Honest evaluation.** Every model is scored with standard metrics (accuracy, R², MAE, RMSE), so results can be trusted and compared.
- **Compare models quickly.** Switch algorithms and see the effect straight away.
- **Actionable insights.** The tool explains what drives price or sales and how unemployment changed after Covid-19, not only raw numbers.
- **Bring your own data.** Upload the official CSV for Tasks 2 to 4 and the whole dashboard updates.
- **Portfolio ready.** A clean, consistent design that works well in a GitHub repo, a LinkedIn demo video and an internship submission.

---

## 3. What's new in this version

- Every page has **tabs** (Data, Explore, Models, Predict, Insights) and a 4-step guide, so it is easy to follow.
- Choose the **sample dataset or upload your own CSV / Excel file** on every page, including Iris.
- Proper charts: distributions, correlation bars and heatmaps, scatter with trend line, box plots, confusion matrix, actual-vs-predicted, error histogram, feature importance, seasonality and region heatmaps.
- **Three models compared** with shuffled 5-fold cross-validation; the best one is picked for you.
- **Column mapping** for the unemployment page, so different file layouts still work.
- Plain-language **insights** and downloadable reports.
- Tested with real public files (CarPrice, Advertising) uploaded through the browser.

---

## 3b. Features

### Task 1: Iris Flower Classification
- Choose between **Random Forest**, **K-Nearest Neighbors** and **Logistic Regression**.
- Adjust the test-set size with a slider.
- See test accuracy, train/test row counts and 5-fold cross-validation accuracy.
- View the confusion matrix, per-class classification report and a feature scatter matrix.
- **Live predictor:** move the four sliders (sepal and petal length and width) to get the predicted species instantly.

### Task 2: Unemployment Analysis
- Filter by region or state.
- KPI cards: overall average, pre-Covid average, Covid-era average (with change in points) and the peak rate.
- Trend line over time with a marker at the national lockdown (25 March 2020).
- Average rate per region, before vs during Covid.
- Seasonal pattern by month.
- Automatically written key insights for policy discussion.

### Tasks 3 and 4: Car Price and Sales Prediction
- Pick the target column to predict.
- Automatic data preparation: removes missing rows, one-hot encodes categories, turns `Year` into `Car_Age` and skips long text columns such as car names.
- Trains **Linear Regression** and **Random Forest**, then picks the best one by R².
- Shows R², MAE and RMSE, an actual vs predicted chart and the top drivers of the target.
- Linear model coefficients show the effect of a one-unit change in each feature.
- **Live prediction form:** enter values and get a predicted price or sales figure.
- Download the model comparison as a CSV.

---

## 4. How to Use

### Requirements
- Python 3.10 or newer
- pip

### Install and run
```bash
# 1. Open a terminal in the project folder (the one containing app.py)
cd "Data Science Intern"

# 2. (Optional) create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install the libraries
pip install -r requirements.txt

# 4. Start the dashboard
streamlit run app.py
```

The app opens in your browser at **http://localhost:8501**.

### Using the dashboard
1. Use the **sidebar** to open a page: Overview, Task 1, Task 2, Task 3 or Task 4.
2. **Task 1** works straight away because Iris data is built into scikit-learn.
3. For **Tasks 2, 3 and 4**, click **Upload the official CodeAlpha CSV** and choose your dataset. Until you upload, the page shows clearly labelled **demo (synthetic) data** so you can try the features.
4. Change the model, test size or filters and watch the metrics and charts update.
5. Use the **live prediction** section at the bottom of each page to try your own inputs.

### Expected dataset columns
The app finds columns by name, so the official CodeAlpha files should work as they are.

| Task | Columns used |
|------|--------------|
| 2. Unemployment | A column with "date" in its name, one containing "unemployment" and "rate", and optionally "region" or "state" |
| 3. Car price | Numeric and categorical car features plus the price column (for example `Selling_Price`) |
| 4. Sales | Numeric advertising columns plus the sales column (for example `Sales`) |

If your file uses very different column names, rename them in the CSV or adjust the matching in `app.py`.

---

## 5. Project Structure

```
CodeAlpha_DataScienceSuite/
├── app.py              # The full dashboard (all four tasks)
├── requirements.txt    # Python dependencies
├── data/               # Real sample datasets (car prices, advertising sales)
├── .streamlit/
│   └── config.toml     # Navy / ice theme
├── projects/
│   └── insighthub/     # Separate Java + Python analytics project
├── LICENSE             # MIT
└── README.md           # This file
```

---

## 6. Metrics Explained

| Metric | Meaning | Good value |
|--------|---------|------------|
| Accuracy | Share of correct predictions (classification) | Closer to 100% |
| Cross-validation accuracy | Accuracy averaged over 5 different splits, a more reliable estimate | Close to test accuracy |
| R² | How much of the variation the model explains (regression) | Closer to 1 |
| MAE | Average size of the error, in the target's own units | Lower is better |
| RMSE | Like MAE but penalises large errors more | Lower is better |

---

## 7. Tech Stack

- **Python** for the logic
- **pandas and NumPy** for data handling
- **scikit-learn** for models and evaluation
- **Plotly** for interactive charts
- **Streamlit** for the web dashboard

---

## 8. Deploy Online (Streamlit Community Cloud)

1. Push `app.py`, `requirements.txt` and `README.md` to a public GitHub repository, ideally in the repo root.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app**, choose your repository and branch `main`, and set the main file path to `app.py`. If the files are in a subfolder, use `Folder Name/app.py`.
4. Click **Deploy**. After a few minutes you get a public `.streamlit.app` link.

---

## 9. Notes and Limitations

- Demo data for Tasks 2 to 4 is **synthetic** and only for trying the features. Use the official datasets for results you plan to submit.
- Models use sensible defaults and a fixed random seed, so results are repeatable. They are not heavily tuned.
- Predictions are only as good as the data. Treat them as estimates, not guarantees.

---

## 10. Internship Submission Checklist

- [ ] Share your internship status on LinkedIn and tag **@CodeAlpha**
- [ ] Upload the source code to GitHub in a repository named `CodeAlpha_ProjectName`
- [ ] Post a video explanation of the project on LinkedIn with the GitHub link
- [ ] Submit the task through the form shared in your WhatsApp group
- [ ] Complete at least 2 to 3 of the 4 tasks to be eligible for the certificate

---

## Author

**Syed Muhammad Bilal Hassan**: Data Science Intern, CodeAlpha
GitHub: [Bilalhassan-it](https://github.com/Bilalhassan-it)
