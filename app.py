import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import spearmanr


DATA_PATH = "nhanes_health.csv"
NUMERIC_COLUMNS = [
    "age",
    "bmi",
    "waist_cm",
    "systolic_bp",
    "diastolic_bp",
    "hba1c",
    "total_chol",
    "hdl_chol",
    "sleep_hours",
    "sedentary_minutes",
]


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


data = load_data()

st.title("NHANES Health Correlation Explorer")

st.sidebar.header("Filters")
sex = st.sidebar.selectbox("Sex", ["All", "Female", "Male"])

min_age = int(data["age"].min())
max_age = int(data["age"].max())
age_range = st.sidebar.slider(
    "Age range",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age),
)

correlation_method = st.sidebar.selectbox(
    "Correlation method", ["Pearson", "Spearman"]
)

filtered_data = data
if sex != "All":
    filtered_data = filtered_data.loc[filtered_data["sex"] == sex]
filtered_data = filtered_data.loc[
    filtered_data["age"].between(age_range[0], age_range[1])
]

st.header("Data preview")
st.write(
    "This dataset contains 4,433 adults aged 20 and over from NHANES 2017–2018. "
    "Each row represents one participant. Age 80 means 80 or older."
)
st.write(f"Participants matching filters: {len(filtered_data):,}")
st.dataframe(filtered_data, use_container_width=True)

st.header("Pairwise view")
plot_col_x, plot_col_y = st.columns(2)
with plot_col_x:
    x_column = st.selectbox("X variable", NUMERIC_COLUMNS, index=0)
with plot_col_y:
    y_column = st.selectbox("Y variable", NUMERIC_COLUMNS, index=3)

trend_choice = st.radio(
    "Trend display", ["Fitted line", "Binned means"], horizontal=True
)
thresholds = {
    "Off": None,
    "Systolic BP >= 130": ("systolic_bp", 130),
    "Diastolic BP >= 80": ("diastolic_bp", 80),
    "BMI >= 30": ("bmi", 30),
    "HbA1c >= 6.5": ("hba1c", 6.5),
    "Total cholesterol >= 240": ("total_chol", 240),
}
threshold_choice = st.selectbox("Color points by health threshold", thresholds)

if x_column == y_column:
    st.info("Pick two different variables for X and Y.")
else:
    pair_data = filtered_data.loc[
        filtered_data[x_column].notna() & filtered_data[y_column].notna()
    ].copy()
    pair_count = len(pair_data)

    if pair_count < 3:
        st.warning(f"r unavailable: fewer than 3 participants have both values (n = {pair_count:,}).")
    elif pair_data[x_column].nunique() < 2 or pair_data[y_column].nunique() < 2:
        st.write(f"r = undefined · n = {pair_count:,} (a variable is constant)")
    else:
        if correlation_method == "Pearson":
            correlation = pair_data[x_column].corr(pair_data[y_column])
        else:
            correlation = spearmanr(pair_data[x_column], pair_data[y_column]).statistic
        st.write(f"{correlation_method} r = {correlation:.3f} · n = {pair_count:,}")

    if pair_count:
        figure, axes = plt.subplots()
        threshold = thresholds[threshold_choice]
        if threshold is None:
            axes.scatter(
                pair_data[x_column], pair_data[y_column], alpha=0.5, s=20
            )
        else:
            threshold_column, cutoff = threshold
            values = pair_data[threshold_column]
            groups = {
                "Below threshold": values.notna() & (values < cutoff),
                "At or above threshold": values.notna() & (values >= cutoff),
                "Unknown": values.isna(),
            }
            colors = {
                "Below threshold": "tab:blue",
                "At or above threshold": "tab:orange",
                "Unknown": "tab:gray",
            }
            for label, mask in groups.items():
                if mask.any():
                    axes.scatter(
                        pair_data.loc[mask, x_column],
                        pair_data.loc[mask, y_column],
                        alpha=0.5,
                        s=20,
                        label=label,
                        color=colors[label],
                    )
            axes.legend(title=threshold_choice)

        if pair_count >= 2 and pair_data[x_column].nunique() >= 2:
            if trend_choice == "Fitted line":
                sns.regplot(
                    data=pair_data,
                    x=x_column,
                    y=y_column,
                    scatter=False,
                    ci=None,
                    color="black",
                    ax=axes,
                )
            else:
                bins = pd.cut(pair_data[x_column], bins=10, duplicates="drop")
                bin_means = pair_data.groupby(bins, observed=True)[y_column].mean()
                axes.plot(
                    [interval.mid for interval in bin_means.index],
                    bin_means.to_numpy(),
                    color="black",
                    marker="o",
                    label="Binned mean",
                )

        axes.set_xlabel(x_column)
        axes.set_ylabel(y_column)
        st.pyplot(figure)
        plt.close(figure)

st.header("Correlation heatmap")
heatmap_columns = st.multiselect(
    "Variables to include",
    NUMERIC_COLUMNS,
    default=NUMERIC_COLUMNS[:5],
)

if len(heatmap_columns) < 2:
    st.info("Select at least two variables to show the heatmap.")
else:
    coefficients = pd.DataFrame(
        float("nan"), index=heatmap_columns, columns=heatmap_columns
    )
    annotations = pd.DataFrame("", index=heatmap_columns, columns=heatmap_columns)

    for row_column in heatmap_columns:
        for column in heatmap_columns:
            pair_columns = [row_column, column] if row_column != column else [row_column]
            complete_pair = filtered_data[pair_columns].dropna()
            count = len(complete_pair)
            if count < 3:
                annotations.loc[row_column, column] = f"—\nn={count:,}"
            elif (
                complete_pair[row_column].nunique() < 2
                or complete_pair[column].nunique() < 2
            ):
                annotations.loc[row_column, column] = f"undefined\nn={count:,}"
            else:
                if correlation_method == "Pearson":
                    value = complete_pair[row_column].corr(complete_pair[column])
                else:
                    value = spearmanr(
                        complete_pair[row_column], complete_pair[column]
                    ).statistic
                coefficients.loc[row_column, column] = value
                annotations.loc[row_column, column] = f"r={value:.2f}\nn={count:,}"

    size = max(6, len(heatmap_columns) * 1.25)
    figure, axes = plt.subplots(figsize=(size, size))
    axes.set_facecolor("#eeeeee")
    sns.heatmap(
        coefficients.astype(float),
        vmin=-1,
        vmax=1,
        center=0,
        cmap="coolwarm",
        linewidths=0.5,
        linecolor="white",
        square=True,
        cbar_kws={"label": f"{correlation_method} r"},
        ax=axes,
    )
    for row_index, row_column in enumerate(heatmap_columns):
        for column_index, column in enumerate(heatmap_columns):
            value = coefficients.loc[row_column, column]
            text_color = "white" if pd.notna(value) and abs(value) >= 0.65 else "black"
            axes.text(
                column_index + 0.5,
                row_index + 0.5,
                annotations.loc[row_column, column],
                ha="center",
                va="center",
                color=text_color,
                fontsize=8,
            )
    axes.tick_params(axis="x", labelrotation=45)
    axes.tick_params(axis="y", labelrotation=0)
    figure.tight_layout()
    st.pyplot(figure)
    plt.close(figure)
    st.caption("— means fewer than 3 paired values; undefined means a variable is constant.")
