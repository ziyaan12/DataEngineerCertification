import pandas as pd
import re
from typing import Tuple

def merge_all_data(user_health_path: str,
                   supplement_usage_path: str,
                   experiments_path: str,
                   user_profiles_path: str) -> pd.DataFrame:
    """
    Read, clean and merge the four datasets into a single DataFrame.

    Output columns (in order):
        user_id, date, email, user_age_group, experiment_name,
        supplement_name, dosage_grams, is_placebo,
        average_heart_rate, average_glucose, sleep_hours,
        activity_level
    """

    # LOAD THE DATASETS
    health = pd.read_csv(user_health_path)
    supp = pd.read_csv(supplement_usage_path)
    exps = pd.read_csv(experiments_path)
    prof = pd.read_csv(user_profiles_path)

    # CLEAN CATEGORICAL AND TEXT FIELDS
    # ensure all IDs are consistent strings
    for df in (health, supp, prof):
        df["user_id"] = df["user_id"].astype(str).str.strip()

    # clean and lowercase all emails
    if "email" in prof.columns:
        prof["email"] = prof["email"].astype(str).str.strip().str.lower()

    # standardise supplement names (trim spaces, collapse duplicates, title case)
    if "supplement_name" in supp.columns:
        supp["supplement_name"] = (
            supp["supplement_name"]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.title()
        )

    # normalise dosage units (convert to either 'mg' or 'g')
    if "dosage_unit" in supp.columns:
        supp["dosage_unit"] = (
            supp["dosage_unit"]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({
                "milligram": "mg", "milligrams": "mg", "mgs": "mg",
                "gram": "g", "grams": "g"
            })
        )
        supp.loc[~supp["dosage_unit"].isin(["mg", "g"]), "dosage_unit"] = pd.NA

    # clean experiment names and fix spacing/capitalisation
    exps = exps.rename(columns={"name": "experiment_name"})
    exps["experiment_name"] = (
        exps["experiment_name"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    # CONVERT DATA TYPES
    # convert date columns to datetime
    for df in (health, supp):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # helper function to extract numeric values from messy text
    def _extract_number(series: pd.Series) -> pd.Series:
        s = series.astype(str).str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)
        return pd.to_numeric(s, errors="coerce")

    # clean and convert key numeric fields
    if "average_heart_rate" in health.columns:
        health["average_heart_rate"] = _extract_number(health["average_heart_rate"])
    if "average_glucose" in health.columns:
        health["average_glucose"] = _extract_number(health["average_glucose"])
    if "sleep_hours" in health.columns:
        health["sleep_hours"] = _extract_number(health["sleep_hours"])

    # convert dosage to grams
    supp["dosage"] = pd.to_numeric(supp.get("dosage"), errors="coerce")
    supp["dosage_grams"] = supp["dosage"]
    if "dosage_unit" in supp.columns:
        supp.loc[supp["dosage_unit"].eq("mg"), "dosage_grams"] = supp["dosage"] / 1000.0
        supp.loc[supp["dosage_unit"].isna(), "dosage_grams"] = pd.NA

    # normalise placebo column into boolean format
    def _to_bool(val):
        if pd.isna(val):
            return pd.NA
        if isinstance(val, (int, float)):
            return bool(int(val))
        s = str(val).strip().lower()
        if s in {"true", "t", "1", "yes", "y", "placebo"}:
            return True
        if s in {"false", "f", "0", "no", "n", "control", "non-placebo", "nonplacebo"}:
            return False
        return pd.NA

    if "is_placebo" in supp.columns:
        supp["is_placebo"] = supp["is_placebo"].apply(_to_bool)

    # MERGE ALL DATASETS
    supp = supp.merge(exps[["experiment_id", "experiment_name"]], on="experiment_id", how="left")
    merged = pd.merge(health, supp, on=["user_id", "date"], how="outer")
    merged = merged.merge(prof[["user_id", "email", "age"]], on="user_id", how="left")

    # group users by age bracket
    def _age_group(a):
        if pd.isna(a):
            return "Unknown"
        try:
            a = float(a)
        except:
            return "Unknown"
        if a < 18:
            return "Under 18"
        if a <= 25:
            return "18-25"
        if a <= 35:
            return "26-35"
        if a <= 45:
            return "36-45"
        if a <= 55:
            return "46-55"
        if a <= 65:
            return "56-65"
        return "Over 65"

    merged["user_age_group"] = merged["age"].apply(_age_group)

    # clean experiment names again after merging
    if "experiment_name" in merged.columns:
        merged["experiment_name"] = (
            merged["experiment_name"]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.title()
        ).where(merged["experiment_name"].notna(), pd.NA)
    
    # HANDLE MISSING VALUES
    # fill missing supplement names with "No intake"
    merged["supplement_name"] = (
        merged.get("supplement_name")
        .astype("string")
        .fillna("")
        .str.strip()
        .replace(r"\s+", " ", regex=True)
        .replace("", "No intake")
    )

    # clean up activity levels and keep within 0–99
    merged["activity_level"] = pd.to_numeric(merged.get("activity_level"), errors="coerce").clip(0, 99)
    merged["activity_level"] = merged["activity_level"].round().astype("Int64")

    # drop rows missing key information
    merged = merged[merged["user_id"].notna() & merged["date"].notna() & merged["email"].notna()].copy()

    # FINAL OUTPUT TABLE
    out_cols = [
        "user_id",
        "date",
        "email",
        "user_age_group",
        "experiment_name",
        "supplement_name",
        "dosage_grams",
        "is_placebo",
        "average_heart_rate",
        "average_glucose",
        "sleep_hours",
        "activity_level",
    ]

    # make sure all expected columns exist
    for c in out_cols:
        if c not in merged.columns:
            merged[c] = pd.NA

    # final ordering and cleanup
    out = (
        merged[out_cols]
        .drop_duplicates(subset=out_cols)
        .sort_values(["user_id", "date", "supplement_name"], kind="stable")
        .reset_index(drop=True)
    )

    return out

# EXECUTION AND FILE EXPORT
if __name__ == "__main__":
    # run the main merge function
    df = merge_all_data(
        "user_health_data.csv",
        "supplement_usage.csv",
        "experiments.csv",
        "user_profiles.csv"
    )

    # save results to CSV and Excel (full dataset)
    df.to_csv("merged_output.csv", index=False)
    try:
        df.to_excel("merged_output.xlsx", index=False)
    except Exception:
        pass

    # preview the first few rows for verification
    try:
        from IPython.display import display
        print("Rows:", len(df), "| Columns:", len(df.columns))
        display(df.head(20))
    except Exception:
        print("Rows:", len(df), "| Columns:", len(df.columns))
        print(df.head(20).to_string(index=False))
