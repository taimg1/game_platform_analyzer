import pandas as pd
import statsmodels.api as sm
from typing import List, Dict, Any
from model import ScrapedGameData


class RegressionModel:
    def __init__(self, scraped_records: List[ScrapedGameData]):
        self.df = self._prepare_dataframe(scraped_records)

    def _prepare_dataframe(
        self, scraped_records: List[ScrapedGameData]
    ) -> pd.DataFrame:
        records = []
        for record in scraped_records:
            metadata = record.game.metadata_json or {}
            genres = metadata.get("genres") or []
            genre = genres[0] if genres else None
            publisher = metadata.get("publisher")

            records.append(
                {
                    "price_in_usd": float(record.price_in_usd),
                    "rating": float(record.rating)
                    if record.rating is not None
                    else float("nan"),
                    "availability_status": record.availability_status.value,
                    "platform_id": str(record.platform_id),
                    "genre": genre,
                    "publisher": publisher,
                }
            )

        df = pd.DataFrame(records)
        for col in ["availability_status", "platform_id", "genre", "publisher"]:
            if col in df.columns:
                df[col] = df[col].astype("category")
        return df

    def run_regression(self, dependent: str, independents: List[str]) -> Dict[str, Any]:
        missing = [c for c in [dependent] + independents if c not in self.df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

        df_proc = self.df.copy()

        cats = [c for c in independents if df_proc[c].dtype.name == "category"]
        if cats:
            df_proc = pd.get_dummies(df_proc, columns=cats, drop_first=True)

        for col in df_proc.select_dtypes(include=["bool"]).columns:
            df_proc[col] = df_proc[col].astype(int)

        numeric_cols = df_proc.select_dtypes(include=["number"]).columns.tolist()
        for col in numeric_cols:
            df_proc[col] = pd.to_numeric(df_proc[col], errors="coerce")

        final_inds = []
        for var in independents:
            if var in df_proc.columns:
                final_inds.append(var)
            else:
                final_inds.extend([col for col in df_proc.columns if col.startswith(f"{var}_")])

        cols = [dependent] + final_inds
        df_clean = df_proc.dropna(subset=cols)

        if df_clean.empty:
            raise ValueError("No data after cleaning for regression.")

        X = sm.add_constant(df_clean[final_inds])
        y = df_clean[dependent]

        model = sm.OLS(y, X).fit()

        return {
            "coefficients": model.params.to_dict(),
            "std_errors": model.bse.to_dict(),
            "t_statistics": model.tvalues.to_dict(),
            "p_values": model.pvalues.to_dict(),
            "r_squared": model.rsquared,
            "adj_r_squared": model.rsquared_adj,
            "f_statistic": model.fvalue,
            "f_p_value": model.f_pvalue,
            "n_observations": int(model.nobs),
        }

