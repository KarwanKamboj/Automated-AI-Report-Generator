import google.generativeai as genai
import os
import json
import time

def _compact_summary(summary_dict: dict) -> dict:
    return {
        "rows": summary_dict.get("num_rows"),
        "columns_count": summary_dict.get("num_cols"),
        "columns": summary_dict.get("columns", [])[:40],
        "numerical_columns": summary_dict.get("numerical_cols", [])[:20],
        "categorical_columns": summary_dict.get("categorical_cols", [])[:20],
        "total_missing_values": summary_dict.get("total_missing_values"),
        "missing_percent": summary_dict.get("missing_percent", {}),
        "duplicate_rows": summary_dict.get("duplicate_rows"),
        "top_categories": summary_dict.get("top_categories", {}),
        "outliers": summary_dict.get("outliers", {}),
        "strongest_correlations": summary_dict.get("correlation_pairs", [])[:8],
        "summary_stats": summary_dict.get("summary_stats", {}),
    }

def get_ai_insights(summary_dict: dict, provided_api_key: str = None) -> str:
    api_key = provided_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "" or api_key == "your_gemini_api_key_here":
        return (
            "## AI Insights Unavailable\n"
            "- Please provide a valid Gemini API key to generate AI insights.\n"
            "- The report still includes automated statistics and visual charts."
        )

    try:
        genai.configure(api_key=api_key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)

        prompt = f"""
You are an expert data analyst. Analyze this dataset profile and write useful, practical insights.

Dataset profile:
{json.dumps(_compact_summary(summary_dict), indent=2)}

Write the response in clean Markdown using these sections:
## Executive Summary
## Key Patterns
## Data Quality Notes
## Outliers and Risks
## Recommended Next Steps

Rules:
- Be concise but specific.
- Mention column names when useful.
- Do not invent facts that are not supported by the profile.
- Use bullets under each section.
"""

        for attempt in range(3):
            try:
                response = model.generate_content(prompt)
                return response.text or "No AI insights were returned."
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    time.sleep(5)
                    continue
                raise

    except Exception as e:
        return f"## AI Insight Error\n- Error generating AI insights: {str(e)}"
