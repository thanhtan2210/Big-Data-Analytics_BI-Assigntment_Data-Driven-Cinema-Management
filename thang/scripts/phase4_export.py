import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

EXPORT_MAP = {
    "movies_enriched": "movies_enriched.csv",
    "genre_stats": "genre_stats.csv",
    "decade_stats": "decade_genre_heatmap.csv",
    "year_stats": "year_stats.csv",
    "rating_dist": "rating_distribution.csv",
    "user_segments": "user_segments.csv",
    "segment_genre_preference": "segment_genre_preference.csv",
    "tag_stats": "tag_stats.csv",
    "segment_recommendations": "segment_recommendations.csv",
}


def _normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    # Convert list-like columns into pipe-separated strings to keep CSV BI-friendly.
    for col_name in df.columns:
        if df[col_name].map(lambda val: isinstance(val, list)).any():
            df[col_name] = df[col_name].map(
                lambda val: "|".join(str(item) for item in val) if isinstance(val, list) else val
            )
    return df


def main():
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")
    export_dir = project_root / "visual" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    client = MongoClient(mongo_uri)
    db = client[mongo_db]

    print("=" * 60)
    print("PHASE 4 EXPORT - MONGODB TO CSV")
    print("=" * 60)

    for collection_name, file_name in EXPORT_MAP.items():
        docs = list(db[collection_name].find({}, {"_id": 0}))

        if not docs:
            print(f"[WARN] Collection {collection_name} is empty. Skip export.")
            continue

        df = pd.DataFrame(docs)
        df = _normalize_for_csv(df)

        output_path = export_dir / file_name
        df.to_csv(output_path, index=False)
        print(f"[OK] Exported {collection_name} -> {output_path}")

    print("=" * 60)
    print(f"Done. CSV files are in {export_dir}")


if __name__ == "__main__":
    main()
