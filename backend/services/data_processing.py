import io
import pandas as pd

def is_identifier_column(df, col):
    name = col.lower()
    unique_ratio = df[col].nunique(dropna=True) / max(len(df), 1)

    id_keywords = ["id", "uuid", "guid", "name", "email", "phone", "ticket", "url"]
    if any(keyword in name for keyword in id_keywords):
        return True

    return unique_ratio > 0.9

def _safe_value(value):
    if pd.isna(value):
        return ""
    if hasattr(value, "item"):
        return value.item()
    return value

def process_file(file_bytes: bytes, filename: str):
    try:
        name = filename.lower()
        if name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file format. Please upload CSV or Excel.")

        df.columns = [str(col).strip() for col in df.columns]

        num_rows, num_cols = df.shape
        numerical_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

        analysis_numerical_cols = [
            col for col in numerical_cols
            if not is_identifier_column(df, col)
        ]

        analysis_categorical_cols = [
            col for col in categorical_cols
            if not is_identifier_column(df, col)
        ]


        missing_counts = df.isna().sum()
        missing_values = missing_counts.to_dict()
        missing_percent = ((missing_counts / max(num_rows, 1)) * 100).round(2).to_dict()

        duplicate_rows = int(df.duplicated().sum())

        summary_stats = {}
        if numerical_cols:
            summary_stats["numerical"] = df[numerical_cols].describe().round(3).fillna("").to_dict()
        if categorical_cols:
            summary_stats["categorical"] = df[categorical_cols].describe().fillna("").to_dict()

        top_categories = {}
        for col in categorical_cols[:8]:
            top_categories[col] = df[col].astype(str).value_counts().head(10).to_dict()

        outliers = {}
        for col in numerical_cols:
            series = df[col].dropna()
            if series.empty:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((series < lower) | (series > upper)).sum())
            outliers[col] = {
                "count": count,
                "percent": round((count / max(len(series), 1)) * 100, 2),
                "lower_bound": round(_safe_value(lower), 3),
                "upper_bound": round(_safe_value(upper), 3),
            }

        correlation_pairs = []
        if len(numerical_cols) >= 2:
            corr = df[numerical_cols].corr(numeric_only=True)
            for i, col_a in enumerate(corr.columns):
                for col_b in corr.columns[i + 1:]:
                    value = corr.loc[col_a, col_b]
                    if pd.notna(value):
                        correlation_pairs.append({
                            "columns": [col_a, col_b],
                            "correlation": round(float(value), 3),
                        })
            correlation_pairs = sorted(correlation_pairs, key=lambda x: abs(x["correlation"]), reverse=True)[:10]

        return {
            "status": "success",
            "num_rows": int(num_rows),
            "num_cols": int(num_cols),
            "columns": df.columns.tolist(),
            "numerical_cols": numerical_cols,
            "categorical_cols": categorical_cols,
            "summary_stats": summary_stats,
            "missing_values": missing_values,
            "missing_percent": missing_percent,
            "total_missing_values": int(missing_counts.sum()),
            "duplicate_rows": duplicate_rows,
            "top_categories": top_categories,
            "outliers": outliers,
            "correlation_pairs": correlation_pairs,
            "head": df.head(5).fillna("").to_dict(orient="records"),
        }, df

    except Exception as e:
        return {"status": "error", "message": str(e)}, None
