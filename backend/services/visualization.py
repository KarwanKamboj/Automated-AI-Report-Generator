import base64
import io

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

PALETTE = ["#2563eb", "#10b981", "#f97316", "#7c3aed", "#ef4444", "#14b8a6"]


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=160, facecolor="white")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def _add_chart(charts, key, title, caption, fig):
    charts[key] = {
        "title": title,
        "caption": caption,
        "image": _fig_to_base64(fig),
    }


def _is_identifier_column(df, col):
    name = str(col).lower()
    unique_ratio = df[col].nunique(dropna=True) / max(len(df), 1)

    id_keywords = ["id", "uuid", "guid", "name", "email", "phone", "ticket", "url"]
    if any(keyword in name for keyword in id_keywords):
        return True

    return unique_ratio > 0.9


def _is_continuous_numeric(df, col):
    return pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique(dropna=True) > 10


def _find_target_column(df):
    preferred_names = [
        "target", "label", "class", "category", "outcome", "result",
        "status", "churn", "survived", "purchased", "converted",
        "approved", "default", "fraud"
    ]

    for col in df.columns:
        unique_count = df[col].nunique(dropna=True)
        if str(col).lower() in preferred_names and 2 <= unique_count <= 10:
            return col

    candidates = []
    for col in df.columns:
        unique_count = df[col].nunique(dropna=True)
        unique_ratio = unique_count / max(len(df), 1)

        if 2 <= unique_count <= 10 and unique_ratio <= 0.2 and not _is_identifier_column(df, col):
            candidates.append((col, unique_count))

    if candidates:
        return sorted(candidates, key=lambda item: item[1])[0][0]

    return None


def _ordered_categories(df, col):
    values = df[col].dropna().unique().tolist()
    try:
        return sorted(values)
    except TypeError:
        return sorted(values, key=lambda value: str(value))


def generate_charts(df: pd.DataFrame, summary_dict: dict | None = None) -> dict:
    charts = {}

    raw_numerical_cols = df.select_dtypes(include=["number"]).columns.tolist()
    raw_categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    numerical_cols = [
        col for col in raw_numerical_cols
        if not _is_identifier_column(df, col)
    ]

    categorical_cols = [
        col for col in raw_categorical_cols
        if not _is_identifier_column(df, col) and 2 <= df[col].nunique(dropna=True) <= 30
    ]

    low_card_numeric_cols = [
        col for col in numerical_cols
        if 2 <= df[col].nunique(dropna=True) <= 10
    ]

    grouping_cols = categorical_cols + low_card_numeric_cols

    target_col = _find_target_column(df)

    continuous_numeric_cols = [
        col for col in numerical_cols
        if _is_continuous_numeric(df, col) and col != target_col
    ]

    # 1. Target by category/group chart
    if target_col:
        useful_groups = [
            col for col in grouping_cols
            if col != target_col and 2 <= df[col].nunique(dropna=True) <= 12
        ]

        if useful_groups:
            cat_col = useful_groups[0]
            fig, ax = plt.subplots(figsize=(8, 4.8))
            sns.countplot(data=df, x=cat_col, hue=target_col, ax=ax, palette="viridis")
            ax.set_title(f"{target_col} by {cat_col}", fontsize=14, fontweight="bold")
            ax.set_xlabel(cat_col)
            ax.set_ylabel("Count")
            plt.xticks(rotation=30, ha="right")
            _add_chart(
                charts,
                "target_by_group",
                f"{target_col} by {cat_col}",
                f"Compares {target_col} counts across {cat_col} groups.",
                fig,
            )

        # 2. Target rate by group for binary numeric targets
        if df[target_col].nunique(dropna=True) == 2 and pd.api.types.is_numeric_dtype(df[target_col]):
            rate_groups = [
                col for col in grouping_cols
                if col != target_col and 2 <= df[col].nunique(dropna=True) <= 12
            ]

            if rate_groups:
                cat_col = rate_groups[0]
                rate_df = (
                    df.groupby(cat_col, dropna=False)[target_col]
                    .mean()
                    .reset_index()
                    .sort_values(target_col, ascending=False)
                )

                fig, ax = plt.subplots(figsize=(8, 4.8))
                sns.barplot(data=rate_df, x=cat_col, y=target_col, hue=cat_col, ax=ax, palette="viridis", legend=False)
                ax.set_title(f"Average {target_col} by {cat_col}", fontsize=14, fontweight="bold")
                ax.set_xlabel(cat_col)
                ax.set_ylabel(f"Average {target_col}")
                ax.set_ylim(0, 1)
                plt.xticks(rotation=30, ha="right")
                _add_chart(
                    charts,
                    "target_rate_by_group",
                    f"Average {target_col} by {cat_col}",
                    f"Shows the average {target_col} value across {cat_col} groups.",
                    fig,
                )

        # 3. Continuous numeric variable by target
        if continuous_numeric_cols:
            num_col = continuous_numeric_cols[0]
            fig, ax = plt.subplots(figsize=(8, 4.8))
            sns.boxplot(data=df, x=target_col, y=num_col, hue=target_col, ax=ax, palette="viridis", legend=False)
            ax.set_title(f"{num_col} by {target_col}", fontsize=14, fontweight="bold")
            ax.set_xlabel(target_col)
            ax.set_ylabel(num_col)
            _add_chart(
                charts,
                "numeric_by_target",
                f"{num_col} by {target_col}",
                f"Shows how {num_col} differs across {target_col} groups.",
                fig,
            )

    # 4. Distribution of a continuous numeric column
    if continuous_numeric_cols:
        col = continuous_numeric_cols[0]
        fig, ax = plt.subplots(figsize=(8, 4.8))
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#2563eb")
        ax.set_title(f"Distribution of {col}", fontsize=14, fontweight="bold")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        _add_chart(
            charts,
            "distribution",
            f"Distribution of {col}",
            "Shows spread, skew, and common value ranges.",
            fig,
        )

    # 5. Correlation heatmap
    corr_cols = continuous_numeric_cols + [
        col for col in low_card_numeric_cols
        if col == target_col
    ]

    if len(corr_cols) >= 2:
        corr = df[corr_cols].corr(numeric_only=True)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="vlag", center=0, fmt=".2f", linewidths=0.5, ax=ax)
        ax.set_title("Correlation Heatmap", fontsize=14, fontweight="bold")
        _add_chart(
            charts,
            "correlation_heatmap",
            "Correlation Heatmap",
            "Highlights relationships between useful numerical columns.",
            fig,
        )

    # 6. Missing values
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(12)

    if not missing.empty:
        fig, ax = plt.subplots(figsize=(8, 4.8))
        sns.barplot(x=missing.values, y=missing.index, ax=ax, color="#ef4444")
        ax.set_title("Missing Values by Column", fontsize=14, fontweight="bold")
        ax.set_xlabel("Missing Count")
        ax.set_ylabel("")
        _add_chart(
            charts,
            "missing_values",
            "Missing Values by Column",
            "Shows columns that may need cleaning before analysis.",
            fig,
        )

    # 7. Top category counts
    remaining_categories = [
        col for col in grouping_cols
        if col != target_col and 2 <= df[col].nunique(dropna=True) <= 30
    ]

    if remaining_categories:
        cat_col = max(remaining_categories, key=lambda c: df[c].nunique(dropna=True))
        counts = df[cat_col].astype(str).value_counts().head(10)

        fig, ax = plt.subplots(figsize=(8, 4.8))
        sns.barplot(x=counts.values, y=counts.index, hue=counts.index, ax=ax, palette="viridis", legend=False)
        ax.set_title(f"Top Categories in {cat_col}", fontsize=14, fontweight="bold")
        ax.set_xlabel("Count")
        ax.set_ylabel("")
        _add_chart(
            charts,
            "top_categories",
            f"Top Categories in {cat_col}",
            "Reveals the most frequent groups or labels.",
            fig,
        )

    # 8. Outlier overview
    if continuous_numeric_cols:
        variances = df[continuous_numeric_cols].var(numeric_only=True).sort_values(ascending=False)
        box_cols = variances.head(min(5, len(variances))).index.tolist()

        if box_cols:
            fig, ax = plt.subplots(figsize=(8, 4.8))
            sns.boxplot(data=df[box_cols], ax=ax, color="#2563eb")
            ax.set_title("Outlier Overview", fontsize=14, fontweight="bold")
            ax.set_xlabel("Numeric Columns")
            ax.set_ylabel("Values")
            plt.xticks(rotation=30, ha="right")
            _add_chart(
                charts,
                "outlier_boxplot",
                "Outlier Overview",
                "Compares continuous numeric columns and makes extreme values visible.",
                fig,
            )

    # 9. Scatter relationship
    if len(continuous_numeric_cols) >= 2:
        x_col, y_col = continuous_numeric_cols[:2]

        fig, ax = plt.subplots(figsize=(8, 4.8))
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax, color="#10b981", alpha=0.75)
        ax.set_title(f"{y_col} vs {x_col}", fontsize=14, fontweight="bold")
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        _add_chart(
            charts,
            "scatter_relationship",
            f"{y_col} vs {x_col}",
            "Shows whether two continuous numeric variables move together.",
            fig,
        )

    max_charts = 7
    return dict(list(charts.items())[:max_charts])
