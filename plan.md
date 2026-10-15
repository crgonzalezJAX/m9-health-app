# Health Correlation App plan

The CSV header confirms ten numeric columns: `age`, `bmi`, `waist_cm`, `systolic_bp`, `diastolic_bp`, `hba1c`, `total_chol`, `hdl_chol`, `sleep_hours`, and `sedentary_minutes`. The remaining column, `sex`, is a filter only.

## Build order

1. **Load data and add sidebar controls.** In `app.py`, load `nhanes_health.csv` by relative path. Define the numeric column choices explicitly, excluding `sex`. Add the sex selector (All, Female, Male), inclusive age range slider, and Pearson/Spearman selector. Apply sex and age filters once to create the filtered data used by every view.
2. **Add the data preview.** Show a short dataset description and a table of the filtered rows. Explain that age 80 means 80 or older.
3. **Add the pairwise view.** Provide numeric X and Y dropdowns. If X and Y match, ask the user to choose two different variables and do not show a correlation. Otherwise, use rows in the filtered data where both X and Y are present for the scatter plot, r, and n. Show r and n together. Show a warning instead of r when n is below 3; show `undefined` instead of r when either variable is constant.
4. **Add the trend display choice.** Let the user choose a straight fitted line or binned means. For binned means, use pandas to divide the selected X range into about ten equal-width bins and plot the mean Y in each nonempty bin. Both choices use the same pair-complete filtered rows as the scatter plot. Pearson or Spearman controls the displayed r independently of the trend display.
5. **Add threshold coloring.** Offer Off and the five requested thresholds: `systolic_bp >= 130`, `diastolic_bp >= 80`, `bmi >= 30`, `hba1c >= 6.5`, and `total_chol >= 240`. Color points in the selected pair's filtered scatter data. Give missing threshold values an `Unknown` color; they do not remove participants from the pairwise r or n.
6. **Add the heatmap.** Let users select numeric variables. Require at least two selections; otherwise show a message asking for two or more variables instead of a heatmap. For each square, use the filtered rows where that square's two variables are present, and annotate it with its own r and n. If n is below 3, show a warning marker and n without r; if either variable is constant, show `undefined` and n. Fix the color scale at `vmin=-1`, `vmax=1`, centered at 0.
7. **Verify the finished views.** Change the sex, age, and method controls and confirm that every view responds. Independently compare representative pairwise and heatmap r and n values in pandas. Check the same-variable and too-few-variable messages, both trend choices, missing values, and constant variables.

## Data flow

`CSV -> sex and age filters -> filtered data -> preview / pairwise view / heatmap`. Each correlation uses only rows with both variables present from that filtered data. The pairwise scatter, trend display, threshold colors, r, and n all refer to the selected pair's filtered rows; threshold values may additionally be missing and appear as `Unknown`. No view reads from the unfiltered data after the filters are applied.

Run the app with:

```bash
uv run --with streamlit,pandas,seaborn,scipy streamlit run app.py
```

The straight fitted line remains available when Spearman is selected; Spearman is still the displayed r. Binned means provide another view of relationships that may curve. A constant variable produces `undefined` because its correlation cannot be computed.

## Checklist

1. **All five required features:** Steps 1-6 cover preview, pairwise view, heatmap, filters, and correlation method.
2. **Filtered r and n:** Every calculation starts with the shared filtered data and removes missing values for that pair only.
3. **Sex excluded:** The explicit numeric selection list omits `sex` from dropdowns and the heatmap.
4. **Fixed heatmap colors:** The scale always runs from -1 to 1, centered at 0.
5. **n next to every r:** The pairwise result and every heatmap square show their own r and n; undefined or unavailable r still shows n.
6. **Incremental build:** Loading and filters come first, followed by one feature per step.
7. **Allowed packages only:** The single `app.py` uses Python, Streamlit, pandas, seaborn, matplotlib, and scipy only.
