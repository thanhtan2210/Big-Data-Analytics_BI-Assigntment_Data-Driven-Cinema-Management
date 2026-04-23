import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from math import sqrt
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def _env_list(key: str, default_values):
    raw = os.getenv(key)
    if not raw:
        return default_values
    return [item.strip() for item in raw.split(",") if item.strip()]


def _as_int_list(values):
    return [int(v) for v in values]


def _as_float_list(values):
    return [float(v) for v in values]


def _first_existing_column(df, candidates, cast_type="double"):
    for col_name in candidates:
        if col_name in df.columns:
            return F.expr(f"try_cast(`{col_name}` as {cast_type})")
    return F.lit(None).cast(cast_type)


def _resolve_column_name(df, candidates):
    lower_map = {col_name.lower(): col_name for col_name in df.columns}
    for candidate in candidates:
        found = lower_map.get(candidate.lower())
        if found:
            return found
    return None


def _normalize_genres(df):
    return (
        df.withColumn("genres", F.coalesce(F.col("genres"), F.lit("Unknown")))
        .withColumn(
            "genres",
            F.when(F.trim(F.col("genres")) == "", F.lit("Unknown")).otherwise(F.col("genres")),
        )
        .withColumn(
            "genres",
            F.when(F.col("genres") == "(no genres listed)", F.lit("Unknown")).otherwise(F.col("genres")),
        )
        .withColumn("genres_array", F.split(F.col("genres"), r"\|"))
    )


def _build_movies_enriched(movies_df, ratings_df):
    rating_by_movie = ratings_df.groupBy("movieId").agg(
        F.avg("rating").alias("avg_rating"),
        F.count("rating").alias("rating_count"),
        F.stddev("rating").alias("rating_stddev"),
    )

    movie_base = (
        movies_df.withColumn("movieId", F.col("movieId").cast("int"))
        .withColumn("title", F.coalesce(F.col("title"), F.lit("Unknown Title")))
        .withColumn("title_clean", F.regexp_extract(F.col("title"), r"^(.*)\\s\\((\\d{4})\\)$", 1))
        .withColumn(
            "title_clean",
            F.when(F.trim(F.col("title_clean")) == "", F.col("title")).otherwise(F.col("title_clean")),
        )
        .withColumn("year_text", F.regexp_extract(F.col("title"), r"\\((\\d{4})\\)", 1))
        .withColumn(
            "year",
            F.when(F.col("year_text") != "", F.col("year_text").cast("int")).otherwise(F.lit(None).cast("int")),
        )
        .drop("year_text")
        .withColumn("decade", (F.floor(F.col("year") / 10) * 10).cast("int"))
    )

    movie_base = _normalize_genres(movie_base)

    revenue_col = _first_existing_column(
        movie_base,
        ["revenue", "tmdb_revenue", "box_office", "gross_revenue"],
        "double",
    )
    budget_col = _first_existing_column(
        movie_base,
        ["budget", "tmdb_budget", "production_budget"],
        "double",
    )

    movie_base = (
        movie_base.withColumn("revenue", revenue_col)
        .withColumn("budget", budget_col)
        .withColumn(
            "roi",
            F.when((F.col("budget").isNotNull()) & (F.col("budget") > 0), (F.col("revenue") - F.col("budget")) / F.col("budget")).otherwise(
                F.lit(None).cast("double")
            ),
        )
        .withColumn("imdbId", F.col("imdbId").cast("string"))
        .withColumn("tmdbId", F.col("tmdbId").cast("string"))
    )

    return (
        movie_base.join(rating_by_movie, on="movieId", how="left")
        .select(
            "movieId",
            "title",
            "title_clean",
            "year",
            "decade",
            "genres",
            "genres_array",
            "avg_rating",
            "rating_count",
            "rating_stddev",
            "imdbId",
            "tmdbId",
            "revenue",
            "budget",
            "roi",
        )
        .dropDuplicates(["movieId"])
    )


def _write_mongo(df, db, collection):
    (
        df.write.format("mongodb")
        .mode("overwrite")
        .option("database", db)
        .option("collection", collection)
        .save()
    )


def _build_popularity_recommendations(movies_enriched_df, user_segments_df, top_n):
    ranked_movies_df = (
        movies_enriched_df.select(
            "movieId",
            "title_clean",
            "genres_array",
            F.col("avg_rating").alias("avg_predicted_rating"),
            "avg_rating",
            "rating_count",
        )
        .fillna({"avg_predicted_rating": 0.0, "avg_rating": 0.0, "rating_count": 0})
        .withColumn(
            "rank",
            F.row_number().over(
                Window.orderBy(F.desc("avg_predicted_rating"), F.desc("rating_count"), F.asc("title_clean"))
            ),
        )
        .filter(F.col("rank") <= top_n)
    )

    segment_sizes_df = user_segments_df.groupBy("segment").agg(
        F.count("userId").alias("recommended_to_users")
    )

    return (
        segment_sizes_df.crossJoin(ranked_movies_df)
        .select(
            "segment",
            "movieId",
            "avg_predicted_rating",
            "recommended_to_users",
            "rank",
            "title_clean",
            "genres_array",
            "avg_rating",
        )
        .orderBy("segment", "rank")
    )


def _safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _split_genres(genres_value):
    if not genres_value:
        return ["Unknown"]
    if isinstance(genres_value, list):
        cleaned = [str(item).strip() for item in genres_value if str(item).strip()]
        return cleaned if cleaned else ["Unknown"]
    text = str(genres_value).strip()
    if not text or text == "(no genres listed)":
        return ["Unknown"]

    # Handle TMDB-style serialized objects like
    # "[{'id': 16, 'name': 'Animation'}, {'id': 35, 'name': 'Comedy'}]"
    tmdb_names = re.findall(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", text)
    if tmdb_names:
        return [name.strip() for name in tmdb_names if name.strip()]

    if "|" in text:
        return [item.strip() or "Unknown" for item in text.split("|")]

    if "," in text:
        return [item.strip() or "Unknown" for item in text.split(",")]

    return [text]


def _clean_title(title_value):
    text = str(title_value or "Unknown Title")
    match = re.match(r"^(.*)\s\((\d{4})\)$", text)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return text


def _extract_year(title_value):
    match = re.search(r"\((\d{4})\)", str(title_value or ""))
    if match:
        return int(match.group(1))
    return None


def _replace_mongo_collection(db, collection_name, documents):
    collection = db[collection_name]
    collection.delete_many({})
    if documents:
        collection.insert_many(documents)


def _run_fast_mongo_pipeline(
    mongo_uri,
    mongo_db,
    input_movies_collection,
    input_ratings_collection,
    input_tags_collection,
    metrics_dir,
    top_n,
    seed,
    fast_sample_fraction,
):
    client = MongoClient(mongo_uri)
    db = client[mongo_db]

    movies_source = list(db[input_movies_collection].find({}, {"_id": 0}))
    total_ratings = db[input_ratings_collection].estimated_document_count()
    sample_size = max(5000, min(25000, int(total_ratings * fast_sample_fraction)))
    ratings_source = list(db[input_ratings_collection].aggregate([{ "$sample": {"size": sample_size} }]))
    tags_source = list(db[input_tags_collection].find({}, {"_id": 0, "tag": 1}))

    movie_lookup = {}
    movie_rating_stats = defaultdict(lambda: {"sum": 0.0, "sum_sq": 0.0, "count": 0})
    genre_movie_stats = defaultdict(lambda: {"movie_ids": set(), "revenue_sum": 0.0, "budget_sum": 0.0, "roi_sum": 0.0, "movie_count": 0})
    genre_rating_stats = defaultdict(lambda: {"sum": 0.0, "count": 0})
    decade_movie_stats = defaultdict(lambda: {"movie_ids": set(), "revenue_sum": 0.0, "budget_sum": 0.0, "roi_sum": 0.0, "movie_count": 0})
    decade_rating_stats = defaultdict(lambda: {"sum": 0.0, "count": 0})
    year_stats = defaultdict(lambda: {"count": 0, "sum": 0.0, "users": set()})
    rating_dist = Counter()
    user_stats = defaultdict(lambda: {"count": 0, "sum": 0.0, "movies": set()})
    segment_genre_stats = defaultdict(lambda: defaultdict(lambda: {"count": 0, "sum": 0.0}))

    for movie in movies_source:
        movie_id = _safe_int(movie.get("movieId") or movie.get("movie_id") or movie.get("id"))
        if movie_id is None:
            continue

        title = movie.get("title") or "Unknown Title"
        title_clean = _clean_title(title)
        year = _extract_year(title)
        decade = int(year // 10 * 10) if year else None
        genres_array = _split_genres(movie.get("genres") or movie.get("genre"))
        revenue = _safe_float(movie.get("revenue") or movie.get("tmdb_revenue") or movie.get("box_office") or movie.get("gross_revenue"))
        budget = _safe_float(movie.get("budget") or movie.get("tmdb_budget") or movie.get("production_budget"))
        roi = ((revenue - budget) / budget) if revenue is not None and budget not in (None, 0) else None

        movie_lookup[movie_id] = {
            "movieId": movie_id,
            "title": title,
            "title_clean": title_clean,
            "year": year,
            "decade": decade,
            "genres": "|".join(genres_array),
            "genres_array": genres_array,
            "revenue": revenue,
            "budget": budget,
            "roi": roi,
        }

        for genre in genres_array:
            genre_movie_stats[genre]["movie_ids"].add(movie_id)
            genre_movie_stats[genre]["movie_count"] += 1
            if revenue is not None:
                genre_movie_stats[genre]["revenue_sum"] += revenue
            if budget is not None:
                genre_movie_stats[genre]["budget_sum"] += budget
            if roi is not None:
                genre_movie_stats[genre]["roi_sum"] += roi

            if decade is not None:
                decade_movie_stats[(decade, genre)]["movie_ids"].add(movie_id)
                decade_movie_stats[(decade, genre)]["movie_count"] += 1
                if revenue is not None:
                    decade_movie_stats[(decade, genre)]["revenue_sum"] += revenue
                if budget is not None:
                    decade_movie_stats[(decade, genre)]["budget_sum"] += budget
                if roi is not None:
                    decade_movie_stats[(decade, genre)]["roi_sum"] += roi

    for rating_doc in ratings_source:
        user_id = _safe_int(rating_doc.get("userId") or rating_doc.get("user_id") or rating_doc.get("userid"))
        movie_id = _safe_int(rating_doc.get("movieId") or rating_doc.get("movie_id") or rating_doc.get("movieid"))
        rating = _safe_float(rating_doc.get("rating") or rating_doc.get("score"))
        timestamp = _safe_int(rating_doc.get("timestamp") or rating_doc.get("createdAt") or rating_doc.get("created_at"))

        if user_id is None or movie_id is None or rating is None:
            continue

        movie_rating_stats[movie_id]["sum"] += rating
        movie_rating_stats[movie_id]["sum_sq"] += rating * rating
        movie_rating_stats[movie_id]["count"] += 1

        user_stats[user_id]["count"] += 1
        user_stats[user_id]["sum"] += rating
        user_stats[user_id]["movies"].add(movie_id)

        rating_dist[rating] += 1

        if timestamp is not None:
            rating_year = datetime.utcfromtimestamp(timestamp).year
            year_stats[rating_year]["count"] += 1
            year_stats[rating_year]["sum"] += rating
            year_stats[rating_year]["users"].add(user_id)

        movie_info = movie_lookup.get(movie_id)
        if movie_info is None:
            continue

        for genre in movie_info["genres_array"]:
            genre_rating_stats[genre]["sum"] += rating
            genre_rating_stats[genre]["count"] += 1

            if movie_info["decade"] is not None:
                decade_rating_stats[(movie_info["decade"], genre)]["sum"] += rating
                decade_rating_stats[(movie_info["decade"], genre)]["count"] += 1

    user_counts = sorted((stats["count"] for stats in user_stats.values()))
    if user_counts:
        q1 = user_counts[max(0, min(len(user_counts) - 1, int(len(user_counts) * 0.33)))]
        q2 = user_counts[max(0, min(len(user_counts) - 1, int(len(user_counts) * 0.66)))]
    else:
        q1 = 0
        q2 = 0

    user_segments = {}
    user_segments_docs = []
    for user_id, stats in user_stats.items():
        rating_count = stats["count"]
        avg_rating = stats["sum"] / rating_count if rating_count else 0.0
        if rating_count >= q2:
            segment = "Heavy"
        elif rating_count >= q1:
            segment = "Medium"
        else:
            segment = "Light"
        user_segments[user_id] = segment
        user_segments_docs.append(
            {
                "userId": user_id,
                "segment": segment,
                "rating_count": rating_count,
                "avg_rating": avg_rating,
                "unique_movies_rated": len(stats["movies"]),
            }
        )

    for rating_doc in ratings_source:
        user_id = _safe_int(rating_doc.get("userId") or rating_doc.get("user_id") or rating_doc.get("userid"))
        movie_id = _safe_int(rating_doc.get("movieId") or rating_doc.get("movie_id") or rating_doc.get("movieid"))
        rating = _safe_float(rating_doc.get("rating") or rating_doc.get("score"))
        segment = user_segments.get(user_id)
        movie_info = movie_lookup.get(movie_id)
        if segment is None or movie_info is None or rating is None:
            continue
        for genre in movie_info["genres_array"]:
            segment_genre_stats[segment][genre]["count"] += 1
            segment_genre_stats[segment][genre]["sum"] += rating

    movies_enriched_docs = []
    for movie_id, movie_info in movie_lookup.items():
        stats = movie_rating_stats.get(movie_id, {"sum": 0.0, "sum_sq": 0.0, "count": 0})
        count = stats["count"]
        avg_rating = stats["sum"] / count if count else None
        rating_stddev = None
        if count > 1 and avg_rating is not None:
            variance = (stats["sum_sq"] / count) - (avg_rating * avg_rating)
            rating_stddev = sqrt(variance) if variance > 0 else 0.0
        movies_enriched_docs.append(
            {
                **movie_info,
                "avg_rating": avg_rating,
                "rating_count": count,
                "rating_stddev": rating_stddev,
            }
        )

    genre_stats_docs = []
    for genre, stats in genre_movie_stats.items():
        rating_stats = genre_rating_stats.get(genre, {"sum": 0.0, "count": 0})
        rating_count = rating_stats["count"]
        genre_stats_docs.append(
            {
                "genre": genre,
                "avg_rating": (rating_stats["sum"] / rating_count) if rating_count else None,
                "rating_count": rating_count,
                "movie_count": len(stats["movie_ids"]),
                "total_revenue": stats["revenue_sum"],
                "avg_revenue": (stats["revenue_sum"] / stats["movie_count"]) if stats["movie_count"] else None,
                "avg_budget": (stats["budget_sum"] / stats["movie_count"]) if stats["movie_count"] else None,
                "avg_roi": (stats["roi_sum"] / stats["movie_count"]) if stats["movie_count"] else None,
            }
        )

    decade_stats_docs = []
    for (decade, genre), stats in decade_movie_stats.items():
        rating_stats = decade_rating_stats.get((decade, genre), {"sum": 0.0, "count": 0})
        rating_count = rating_stats["count"]
        decade_stats_docs.append(
            {
                "decade": decade,
                "genre": genre,
                "avg_rating": (rating_stats["sum"] / rating_count) if rating_count else None,
                "rating_count": rating_count,
                "movie_count": len(stats["movie_ids"]),
                "avg_revenue": (stats["revenue_sum"] / stats["movie_count"]) if stats["movie_count"] else None,
            }
        )

    year_stats_docs = []
    for rating_year, stats in sorted(year_stats.items()):
        year_stats_docs.append(
            {
                "rating_year": rating_year,
                "rating_count": stats["count"],
                "avg_rating": (stats["sum"] / stats["count"]) if stats["count"] else None,
                "active_users": len(stats["users"]),
            }
        )

    rating_dist_docs = [{"rating": rating, "frequency": frequency} for rating, frequency in sorted(rating_dist.items())]

    segment_genre_docs = []
    for segment, genre_map in segment_genre_stats.items():
        ranking = sorted(genre_map.items(), key=lambda item: (-item[1]["count"], -(item[1]["sum"] / item[1]["count"] if item[1]["count"] else 0.0), item[0]))
        for rank, (genre, stats) in enumerate(ranking, start=1):
            segment_genre_docs.append(
                {
                    "segment": segment,
                    "genre": genre,
                    "rating_count": stats["count"],
                    "avg_rating": (stats["sum"] / stats["count"]) if stats["count"] else None,
                    "genre_rank": rank,
                }
            )

    tag_stats_docs = []
    tag_counter = Counter()
    for tag_doc in tags_source:
        tag_value = str(tag_doc.get("tag") or "").strip().lower()
        if tag_value:
            tag_counter[tag_value] += 1
    for tag, frequency in sorted(tag_counter.items(), key=lambda item: (-item[1], item[0])):
        tag_stats_docs.append({"tag": tag, "frequency": frequency})

    ranked_movies = sorted(
        movies_enriched_docs,
        key=lambda item: (
            -(item["avg_rating"] or 0.0),
            -(item["rating_count"] or 0),
            item["title_clean"],
        ),
    )[:top_n]
    segment_sizes = Counter(user_segments.values())
    segment_recommendations_docs = []
    for segment, recommended_to_users in sorted(segment_sizes.items()):
        for rank, movie in enumerate(ranked_movies, start=1):
            segment_recommendations_docs.append(
                {
                    "segment": segment,
                    "movieId": movie["movieId"],
                    "avg_predicted_rating": movie["avg_rating"] or 0.0,
                    "recommended_to_users": recommended_to_users,
                    "rank": rank,
                    "title_clean": movie["title_clean"],
                    "genres_array": movie["genres_array"],
                    "avg_rating": movie["avg_rating"],
                }
            )

    _replace_mongo_collection(db, "movies_enriched", movies_enriched_docs)
    _replace_mongo_collection(db, "genre_stats", genre_stats_docs)
    _replace_mongo_collection(db, "decade_stats", decade_stats_docs)
    _replace_mongo_collection(db, "year_stats", year_stats_docs)
    _replace_mongo_collection(db, "rating_dist", rating_dist_docs)
    _replace_mongo_collection(db, "user_segments", user_segments_docs)
    _replace_mongo_collection(db, "segment_genre_preference", segment_genre_docs)
    _replace_mongo_collection(db, "tag_stats", tag_stats_docs)
    _replace_mongo_collection(db, "segment_recommendations", segment_recommendations_docs)

    metrics_payload = {
        "best_validation": {"mode": "fast_mongo_fallback", "top_n": top_n, "sample_fraction": fast_sample_fraction},
        "test_rmse": None,
        "trials": [],
        "train_count": None,
        "validation_count": None,
        "test_count": None,
        "top_n": top_n,
        "als_sample_fraction": fast_sample_fraction,
        "fast_mode": True,
        "fast_path": "pymongo",
        "sample_size": sample_size,
    }

    with (metrics_dir / "als_metrics.json").open("w", encoding="utf-8") as fh:
        json.dump(metrics_payload, fh, indent=2)

    print("Fast MongoDB path completed successfully.")
    print("Saved metrics to:", metrics_dir / "als_metrics.json")


def main():
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
    mongo_db = os.getenv("MONGO_DB", "cinema_dw")

    input_movies_collection = os.getenv("PHASE2_MOVIES_COLLECTION", "movies")
    input_ratings_collection = os.getenv("PHASE2_RATINGS_COLLECTION", "ratings")
    input_tags_collection = os.getenv("PHASE2_TAGS_COLLECTION", "tags")

    rank_grid = _as_int_list(_env_list("ALS_RANK_GRID", [20, 40]))
    reg_grid = _as_float_list(_env_list("ALS_REG_GRID", [0.05, 0.1]))
    iter_grid = _as_int_list(_env_list("ALS_MAX_ITER_GRID", [10, 15]))
    top_n = int(os.getenv("ALS_TOP_N", "10"))
    seed = int(os.getenv("ALS_SEED", "42"))
    als_sample_fraction = float(os.getenv("ALS_SAMPLE_FRACTION", "0.2"))
    fast_sample_fraction = float(os.getenv("TASK3_FAST_SAMPLE_FRACTION", "0.0005"))
    fast_mode = os.getenv("TASK3_FAST_MODE", "0").lower() in {"1", "true", "yes"}
    train_df = None
    val_df = None
    test_df = None

    metrics_dir = project_root / "thang" / "artifacts" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    if fast_mode:
        _run_fast_mongo_pipeline(
            mongo_uri,
            mongo_db,
            input_movies_collection,
            input_ratings_collection,
            input_tags_collection,
            metrics_dir,
            top_n,
            seed,
            fast_sample_fraction,
        )
        return

    spark = (
        SparkSession.builder.appName("Task3_Analytics_Recommendation_Modeling")
        .config("spark.mongodb.read.connection.uri", mongo_uri)
        .config("spark.mongodb.write.connection.uri", mongo_uri)
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    print("=" * 70)
    print("TASK 3 - ANALYTICS & RECOMMENDATION MODELING")
    print("=" * 70)

    movies_df = (
        spark.read.format("mongodb")
        .option("database", mongo_db)
        .option("collection", input_movies_collection)
        .load()
    )
    ratings_df = (
        spark.read.format("mongodb")
        .option("database", mongo_db)
        .option("collection", input_ratings_collection)
        .load()
    )
    tags_df = (
        spark.read.format("mongodb")
        .option("database", mongo_db)
        .option("collection", input_tags_collection)
        .load()
    )

    user_col = _resolve_column_name(ratings_df, ["userId", "user_id", "userid"])
    movie_col = _resolve_column_name(ratings_df, ["movieId", "movie_id", "movieid"])
    rating_col = _resolve_column_name(ratings_df, ["rating", "score"])
    ts_col = _resolve_column_name(ratings_df, ["timestamp", "createdAt", "created_at"])

    if not user_col or not movie_col or not rating_col:
        raise RuntimeError(
            "ratings collection schema is incompatible. "
            f"Found columns: {ratings_df.columns}. "
            "Need userId/movieId/rating (or accepted aliases)."
        )

    selected_cols = [
        F.col(user_col).cast("int").alias("userId"),
        F.col(movie_col).cast("int").alias("movieId"),
        F.col(rating_col).cast("double").alias("rating"),
    ]
    if ts_col:
        selected_cols.append(F.col(ts_col).cast("long").alias("timestamp"))
    else:
        selected_cols.append(F.lit(None).cast("long").alias("timestamp"))

    ratings_df = ratings_df.select(*selected_cols).filter(
        F.col("userId").isNotNull() & F.col("movieId").isNotNull() & F.col("rating").isNotNull()
    )

    analytics_ratings_df = ratings_df
    if fast_mode and 0 < fast_sample_fraction < 1:
        analytics_ratings_df = ratings_df.sample(withReplacement=False, fraction=fast_sample_fraction, seed=seed)

    movies_enriched_df = _build_movies_enriched(movies_df, analytics_ratings_df)
    genre_movie_df = movies_enriched_df.select(
        "movieId",
        "decade",
        "revenue",
        "budget",
        "roi",
        F.explode_outer("genres_array").alias("genre"),
    ).withColumn("genre", F.coalesce(F.col("genre"), F.lit("Unknown")))

    genre_revenue_df = genre_movie_df.groupBy("genre").agg(
        F.count_distinct("movieId").alias("movie_count"),
        F.sum("revenue").alias("total_revenue"),
        F.avg("revenue").alias("avg_revenue"),
        F.avg("budget").alias("avg_budget"),
        F.avg("roi").alias("avg_roi"),
    )

    rating_with_genre_df = analytics_ratings_df.join(
        genre_movie_df.select("movieId", "genre"), on="movieId", how="inner"
    )
    genre_rating_df = rating_with_genre_df.groupBy("genre").agg(
        F.avg("rating").alias("avg_rating"),
        F.count("rating").alias("rating_count"),
    )

    genre_stats_df = (
        genre_rating_df.join(genre_revenue_df, on="genre", how="outer")
        .fillna({"movie_count": 0, "rating_count": 0})
        .orderBy(F.desc("total_revenue"), F.desc("rating_count"))
    )

    decade_revenue_df = genre_movie_df.groupBy("decade", "genre").agg(
        F.avg("revenue").alias("avg_revenue"),
        F.count_distinct("movieId").alias("movie_count"),
    )
    decade_rating_df = analytics_ratings_df.join(
        genre_movie_df.select("movieId", "decade", "genre"), on="movieId", how="inner"
    ).groupBy("decade", "genre").agg(
        F.avg("rating").alias("avg_rating"),
        F.count("rating").alias("rating_count"),
    )
    decade_stats_df = (
        decade_rating_df.join(decade_revenue_df, on=["decade", "genre"], how="outer")
        .fillna({"movie_count": 0, "rating_count": 0})
        .orderBy("decade", F.desc("rating_count"))
    )

    year_stats_df = (
        analytics_ratings_df.withColumn("rating_year", F.year(F.from_unixtime(F.col("timestamp"))))
        .groupBy("rating_year")
        .agg(
            F.count("rating").alias("rating_count"),
            F.avg("rating").alias("avg_rating"),
            F.count_distinct("userId").alias("active_users"),
        )
        .orderBy("rating_year")
    )

    rating_dist_df = analytics_ratings_df.groupBy("rating").agg(F.count("rating").alias("frequency")).orderBy("rating")

    user_segments_df = analytics_ratings_df.groupBy("userId").agg(
        F.count("rating").alias("rating_count"),
        F.avg("rating").alias("avg_rating"),
        F.count_distinct("movieId").alias("unique_movies_rated"),
    )

    quantiles = user_segments_df.approxQuantile("rating_count", [0.33, 0.66], 0.01)
    q1, q2 = quantiles[0], quantiles[1]
    user_segments_df = user_segments_df.withColumn(
        "segment",
        F.when(F.col("rating_count") >= F.lit(q2), F.lit("Heavy"))
        .when(F.col("rating_count") >= F.lit(q1), F.lit("Medium"))
        .otherwise(F.lit("Light")),
    ).select("userId", "segment", "rating_count", "avg_rating", "unique_movies_rated")

    segment_genre_df = (
        analytics_ratings_df.join(user_segments_df.select("userId", "segment"), on="userId", how="inner")
        .join(genre_movie_df.select("movieId", "genre"), on="movieId", how="inner")
        .groupBy("segment", "genre")
        .agg(F.count("rating").alias("rating_count"), F.avg("rating").alias("avg_rating"))
    )
    seg_rank_window = Window.partitionBy("segment").orderBy(F.desc("rating_count"), F.desc("avg_rating"))
    segment_genre_preference_df = segment_genre_df.withColumn(
        "genre_rank", F.row_number().over(seg_rank_window)
    )

    tag_stats_df = (
        tags_df.select(F.lower(F.trim(F.col("tag"))).alias("tag"))
        .filter(F.col("tag").isNotNull() & (F.col("tag") != ""))
        .groupBy("tag")
        .agg(F.count("tag").alias("frequency"))
        .orderBy(F.desc("frequency"), F.asc("tag"))
    )

    if fast_mode:
        tuning_results = []
        best_config = {"mode": "fast_popularity_fallback", "top_n": top_n, "sample_fraction": als_sample_fraction}
        test_rmse = None
        segment_recommendations_df = _build_popularity_recommendations(movies_enriched_df, user_segments_df, top_n)
    else:
        # Keep full data for analytics, but optionally downsample ALS training data for local resource limits.
        als_ratings_df = ratings_df
        if 0 < als_sample_fraction < 1:
            als_ratings_df = ratings_df.sample(withReplacement=False, fraction=als_sample_fraction, seed=seed)

        train_df, val_df, test_df = als_ratings_df.randomSplit([0.8, 0.1, 0.1], seed=seed)

        evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
        tuning_results = []
        best_rmse = float("inf")
        best_model = None
        best_config = None

        for rank in rank_grid:
            for reg in reg_grid:
                for max_iter in iter_grid:
                    als = ALS(
                        userCol="userId",
                        itemCol="movieId",
                        ratingCol="rating",
                        rank=rank,
                        regParam=reg,
                        maxIter=max_iter,
                        coldStartStrategy="drop",
                        nonnegative=True,
                        seed=seed,
                    )
                    model = als.fit(train_df)
                    val_pred = model.transform(val_df)
                    rmse = evaluator.evaluate(val_pred)

                    trial = {"rank": rank, "regParam": reg, "maxIter": max_iter, "validation_rmse": rmse}
                    tuning_results.append(trial)

                    if rmse < best_rmse:
                        best_rmse = rmse
                        best_model = model
                        best_config = trial

        if best_model is None:
            raise RuntimeError("ALS tuning failed: no valid model was trained. Check input ratings and ALS grid.")

        test_pred = best_model.transform(test_df)
        test_rmse = evaluator.evaluate(test_pred)

        recommendations_df = best_model.recommendForAllUsers(top_n).select(
            "userId", F.explode("recommendations").alias("rec")
        ).select(
            "userId",
            F.col("rec.movieId").cast("int").alias("movieId"),
            F.col("rec.rating").cast("double").alias("predicted_rating"),
        )

        segment_recommendations_df = (
            recommendations_df.join(user_segments_df.select("userId", "segment"), on="userId", how="inner")
            .groupBy("segment", "movieId")
            .agg(
                F.avg("predicted_rating").alias("avg_predicted_rating"),
                F.count_distinct("userId").alias("recommended_to_users"),
            )
        )

        rec_rank_window = Window.partitionBy("segment").orderBy(
            F.desc("avg_predicted_rating"), F.desc("recommended_to_users")
        )
        segment_recommendations_df = (
            segment_recommendations_df.withColumn("rank", F.row_number().over(rec_rank_window))
            .filter(F.col("rank") <= top_n)
            .join(
                movies_enriched_df.select("movieId", "title_clean", "genres_array", "avg_rating"),
                on="movieId",
                how="left",
            )
            .select(
                "segment",
                "movieId",
                "avg_predicted_rating",
                "recommended_to_users",
                "rank",
                "title_clean",
                "genres_array",
                "avg_rating",
            )
            .orderBy("segment", "rank")
        )

    print("Writing Task 3 collections to MongoDB...")
    _write_mongo(movies_enriched_df, mongo_db, "movies_enriched")
    _write_mongo(genre_stats_df, mongo_db, "genre_stats")
    _write_mongo(decade_stats_df, mongo_db, "decade_stats")
    _write_mongo(year_stats_df, mongo_db, "year_stats")
    _write_mongo(rating_dist_df, mongo_db, "rating_dist")
    _write_mongo(user_segments_df, mongo_db, "user_segments")
    _write_mongo(segment_genre_preference_df, mongo_db, "segment_genre_preference")
    _write_mongo(tag_stats_df, mongo_db, "tag_stats")
    _write_mongo(segment_recommendations_df, mongo_db, "segment_recommendations")

    metrics_payload = {
        "best_validation": best_config,
        "test_rmse": test_rmse,
        "trials": sorted(tuning_results, key=lambda item: item["validation_rmse"]),
        "train_count": train_df.count() if train_df is not None else None,
        "validation_count": val_df.count() if val_df is not None else None,
        "test_count": test_df.count() if test_df is not None else None,
        "top_n": top_n,
        "als_sample_fraction": als_sample_fraction,
        "fast_mode": fast_mode,
    }

    with (metrics_dir / "als_metrics.json").open("w", encoding="utf-8") as fh:
        json.dump(metrics_payload, fh, indent=2)

    print("Best ALS config:", best_config)
    print("Test RMSE:", test_rmse)
    print("Saved metrics to:", metrics_dir / "als_metrics.json")
    print("Task 3 pipeline completed successfully.")

    spark.stop()


if __name__ == "__main__":
    main()
