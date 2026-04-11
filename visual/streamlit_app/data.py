"""
data.py — Mock data generators for Cinema BI Streamlit prototype.
All functions return a pandas DataFrame matching the schema defined in
visual/DASHBOARDS.md and visual/CONNECTION_GUIDE.md.
"""
import numpy as np
import pandas as pd

# ── Constants ─────────────────────────────────────────────────────────────────

GENRES = [
    "Action", "Adventure", "Animation", "Children", "Comedy",
    "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir",
    "Horror", "Musical", "Mystery", "Romance", "Sci-Fi",
    "Thriller", "War", "Western",
]

SEGMENTS = ["Heavy", "Medium", "Light"]


# ── Dashboard 1 ───────────────────────────────────────────────────────────────

def get_genre_stats() -> pd.DataFrame:
    """genre-level revenue, rating, and ROI — used by Dashboard 1 & 2."""
    return pd.DataFrame({
        "genre": GENRES,
        "avg_rating": [
            3.79, 3.63, 3.71, 3.50, 3.54, 3.84, 3.92, 3.88,
            3.61, 4.01, 3.41, 3.72, 3.88, 3.61, 3.73, 3.78, 3.91, 3.73,
        ],
        "rating_count": [
            4_512_000, 3_201_000, 812_000, 620_000, 4_988_000,
            2_780_000, 412_000, 6_210_000, 1_502_000, 198_000,
            1_980_000, 498_000, 1_201_000, 2_510_000, 2_201_000,
            3_502_000, 712_000, 402_000,
        ],
        "movie_count": [
            1198, 891, 302, 394, 1982, 801, 347, 2981, 604, 102,
            1002, 202, 502, 1204, 702, 1102, 302, 202,
        ],
        # Revenue / budget in millions USD (from TMDB)
        "total_revenue": [
            84_200, 71_800, 44_500, 17_800, 54_200, 27_500, 3_800,
            41_200, 37_600, 1_400, 21_800, 7_800, 14_800, 19_600,
            64_800, 34_200, 11_800, 5_800,
        ],
        "avg_revenue": [
            420, 378, 276, 88, 179, 128, 17, 93, 238, 21,
            83, 53, 93, 66, 338, 163, 118, 46,
        ],
        "avg_budget": [
            138, 128, 84, 29, 54, 39, 7, 27, 79, 7,
            27, 17, 31, 21, 108, 51, 44, 17,
        ],
        "avg_roi": [
            2.04, 1.95, 2.28, 2.03, 2.31, 2.28, 1.43, 2.44,
            2.01, 2.00, 2.07, 2.12, 2.00, 2.14, 2.13, 2.20, 1.68, 1.71,
        ],
    })


def get_decade_stats() -> pd.DataFrame:
    """decade × genre → avg_rating, rating_count, avg_revenue."""
    genres  = ["Action", "Adventure", "Animation", "Comedy", "Drama",
               "Horror", "Romance", "Sci-Fi", "Thriller"]
    decades = [1950, 1960, 1970, 1980, 1990, 2000, 2010]

    base_rev = {"Action": 120, "Adventure": 95, "Animation": 70, "Comedy": 50,
                "Drama": 30, "Horror": 25, "Romance": 28, "Sci-Fi": 110, "Thriller": 48}
    base_rat = {"Action": 3.6, "Adventure": 3.5, "Animation": 3.65, "Comedy": 3.45,
                "Drama": 3.85, "Horror": 3.3, "Romance": 3.5, "Sci-Fi": 3.65, "Thriller": 3.7}

    rng  = np.random.default_rng(42)
    rows = []
    for d in decades:
        era_factor = 0.15 if d < 1980 else (0.5 if d < 1990 else 1.0)
        for g in genres:
            rev = base_rev[g] * era_factor * rng.uniform(0.85, 1.15)
            rat = float(np.clip(base_rat[g] + rng.uniform(-0.15, 0.15), 2.5, 4.8))
            cnt = int(rng.uniform(5_000, 400_000) * (1 + (d - 1950) / 80))
            rows.append({
                "decade": d, "genre": g,
                "avg_rating":   round(rat, 2),
                "rating_count": cnt,
                "avg_revenue":  round(rev, 1),
                "movie_count":  int(rng.uniform(15, 280)),
            })
    return pd.DataFrame(rows)


def get_top_movies() -> pd.DataFrame:
    """Top 20 movies by revenue for Dashboard 1 table."""
    return pd.DataFrame({
        "title": [
            "Avatar", "Titanic", "Star Wars: The Force Awakens",
            "Avengers: Infinity War", "Jurassic World", "The Lion King (2019)",
            "The Avengers", "Furious 7", "Avengers: Age of Ultron", "Black Panther",
            "Harry Potter: Deathly Hallows Pt 2", "Star Wars: The Last Jedi",
            "Jurassic World: Fallen Kingdom", "Frozen", "Iron Man 3",
            "Transformers: Dark of the Moon", "The Dark Knight Rises",
            "Toy Story 3", "Spider-Man: No Way Home", "The Dark Knight",
        ],
        "genres": [
            "Action|Adventure|Sci-Fi", "Drama|Romance", "Action|Adventure|Sci-Fi",
            "Action|Adventure|Sci-Fi", "Action|Adventure|Sci-Fi", "Animation|Drama",
            "Action|Adventure|Sci-Fi", "Action|Crime|Thriller", "Action|Adventure|Sci-Fi",
            "Action|Adventure|Sci-Fi", "Adventure|Fantasy", "Action|Adventure|Sci-Fi",
            "Action|Adventure|Sci-Fi", "Animation|Comedy|Fantasy|Musical",
            "Action|Adventure|Sci-Fi", "Action|Adventure|Sci-Fi", "Action|Crime|Drama",
            "Animation|Children|Comedy", "Action|Adventure|Sci-Fi", "Action|Crime|Drama",
        ],
        "year": [
            2009, 1997, 2015, 2018, 2015, 2019, 2012, 2015,
            2015, 2018, 2011, 2017, 2018, 2013, 2013,
            2011, 2012, 2010, 2021, 2008,
        ],
        "revenue": [
            2787, 2187, 2068, 2048, 1671, 1656, 1518, 1515,
            1405, 1346, 1341, 1332, 1309, 1280, 1215,
            1123, 1084, 1067, 1901, 1005,
        ],  # millions USD
        "budget": [
            237, 200, 245, 316, 150, 260, 220, 190,
            250, 200, 125, 317, 170, 150, 200,
            195, 250, 200, 200, 185,
        ],
        "roi": [
            10.76, 9.94, 7.44, 5.47, 10.14, 5.37, 5.90, 6.97,
            4.62, 5.73, 9.73, 3.20, 6.70, 7.53, 5.08,
            4.76, 3.34, 4.34, 8.51, 4.43,
        ],
        "avg_rating": [
            3.54, 3.71, 3.87, 4.02, 3.52, 3.64, 3.76, 3.12,
            3.45, 3.88, 4.11, 3.75, 3.22, 3.81, 3.55,
            2.84, 4.08, 4.03, 4.12, 4.28,
        ],
        "rating_count": [
            38_420, 45_820, 32_140, 28_950, 22_840, 31_200, 41_820, 18_640,
            25_840, 18_920, 29_840, 22_150, 14_820, 28_420, 24_180,
            12_840, 42_180, 32_450, 28_100, 58_940,
        ],
    })


# ── Dashboard 2 ───────────────────────────────────────────────────────────────

def get_year_stats() -> pd.DataFrame:
    """Yearly rating activity — used by Dashboard 2."""
    years = list(range(1995, 2020))
    counts = [
        180_000, 320_000, 580_000, 920_000, 1_450_000, 1_820_000,
        2_100_000, 2_350_000, 2_180_000, 2_050_000, 1_820_000, 1_650_000,
        1_480_000, 1_320_000, 1_180_000, 1_050_000, 980_000, 1_120_000,
        1_280_000, 1_350_000, 1_410_000, 1_380_000, 1_290_000, 1_180_000, 1_050_000,
    ]
    return pd.DataFrame({
        "rating_year":  years,
        "rating_count": counts,
        "active_users": [int(c * 0.44) for c in counts],
        "avg_rating":   [round(3.52 + i * 0.004, 3) for i in range(len(years))],
    })


def get_rating_dist() -> pd.DataFrame:
    """Rating value histogram — used by Dashboard 2."""
    return pd.DataFrame({
        "rating":    [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
        "frequency": [
            350_000, 750_000, 640_000, 1_350_000, 1_780_000,
            4_200_000, 5_400_000, 6_100_000, 2_900_000, 1_580_000,
        ],
    })


# ── Dashboard 3 ───────────────────────────────────────────────────────────────

def get_user_segment_summary() -> pd.DataFrame:
    """Aggregate stats per segment — used by Dashboard 3."""
    return pd.DataFrame({
        "segment":    ["Heavy", "Medium", "Light"],
        "user_count": [14_820,  48_210,   99_511],
        "avg_rating": [3.85,    3.71,     3.62],
        "avg_movies": [482,     98,       32],
    })


def get_segment_genre_preference() -> pd.DataFrame:
    """segment × genre rating affinity — used by Dashboard 3."""
    genres = [
        "Drama", "Comedy", "Thriller", "Action", "Romance",
        "Crime", "Sci-Fi", "Horror", "Adventure", "Documentary",
    ]
    counts = {
        "Heavy":  [980_000, 820_000, 760_000, 700_000, 640_000,
                   720_000, 660_000, 420_000, 580_000, 280_000],
        "Medium": [1_800_000, 1_600_000, 1_200_000, 1_400_000, 980_000,
                   980_000, 980_000, 820_000, 1_050_000, 200_000],
        "Light":  [1_100_000, 1_200_000, 700_000, 1_000_000, 680_000,
                   560_000, 560_000, 620_000, 620_000, 100_000],
    }
    ratings = {
        "Heavy":  [3.95, 3.60, 3.82, 3.72, 3.65, 3.88, 3.76, 3.42, 3.62, 4.01],
        "Medium": [3.88, 3.55, 3.78, 3.68, 3.60, 3.82, 3.71, 3.40, 3.58, 3.92],
        "Light":  [3.80, 3.50, 3.70, 3.62, 3.55, 3.74, 3.65, 3.38, 3.52, 3.85],
    }
    rows = []
    for seg in SEGMENTS:
        for rank, g in enumerate(genres, 1):
            rows.append({
                "segment":      seg,
                "genre":        g,
                "rating_count": counts[seg][rank - 1],
                "avg_rating":   ratings[seg][rank - 1],
                "genre_rank":   rank,
            })
    return pd.DataFrame(rows)


def get_tag_stats() -> pd.DataFrame:
    """Top 20 free-text tags — used by Dashboard 3."""
    return pd.DataFrame({
        "tag": [
            "atmospheric", "thought-provoking", "visually stunning", "dark humor",
            "based on a book", "suspenseful", "twist ending", "psychological",
            "sci-fi", "action packed", "emotional", "cult classic", "dark",
            "funny", "historical", "biographical", "violent", "classic",
            "independent film", "superhero",
        ],
        "frequency": [
            28_420, 24_180, 21_500, 19_840, 18_920, 17_640, 16_280, 15_820,
            14_960, 14_320, 13_840, 13_120, 12_680, 12_200, 11_840, 11_420,
            10_980, 10_640, 10_280, 9_840,
        ],
    })


def get_segment_recommendations() -> pd.DataFrame:
    """ALS top-10 recommendations per segment — used by Dashboard 3."""
    pool = {
        "Heavy": [
            ("The Shawshank Redemption", "Drama|Crime", 4.43, 3_800),
            ("Schindler's List",          "Drama|War",     4.41, 3_620),
            ("The Godfather",             "Drama|Crime",   4.40, 3_500),
            ("12 Angry Men",              "Drama",         4.38, 3_210),
            ("Chinatown",                 "Film-Noir|Thriller", 4.19, 2_940),
            ("Apocalypse Now",            "Drama|War",     4.17, 2_800),
            ("Seven Samurai",             "Action|Drama",  4.16, 2_650),
            ("Rear Window",               "Mystery|Thriller", 4.15, 2_520),
            ("2001: A Space Odyssey",     "Drama|Sci-Fi",  4.09, 2_380),
            ("Stalker",                   "Drama|Sci-Fi",  4.08, 2_200),
        ],
        "Medium": [
            ("The Dark Knight",           "Action|Crime|Drama",  4.25, 5_800),
            ("Pulp Fiction",              "Crime|Drama",         4.22, 5_650),
            ("Goodfellas",                "Crime|Drama",         4.20, 5_400),
            ("The Silence of the Lambs",  "Crime|Horror|Thriller", 4.18, 5_100),
            ("Fight Club",                "Crime|Drama|Mystery", 4.17, 4_950),
            ("The Matrix",                "Action|Sci-Fi",       4.15, 4_800),
            ("Forrest Gump",              "Comedy|Drama|Romance", 4.12, 4_620),
            ("The Departed",              "Crime|Drama|Thriller", 4.14, 4_440),
            ("Inception",                 "Action|Crime|Drama",  4.10, 4_280),
            ("Interstellar",              "Sci-Fi|Drama",        4.05, 4_050),
        ],
        "Light": [
            ("The Dark Knight",           "Action|Crime|Drama",  4.20, 12_500),
            ("Avengers: Endgame",         "Action|Adventure|Sci-Fi", 4.02, 11_800),
            ("Forrest Gump",              "Comedy|Drama|Romance", 4.05, 11_250),
            ("The Matrix",                "Action|Sci-Fi",       4.08, 10_900),
            ("Toy Story",                 "Animation|Comedy",    3.98, 10_600),
            ("Inception",                 "Action|Crime|Drama",  4.00, 10_200),
            ("The Lion King",             "Animation|Drama",     3.96, 9_840),
            ("Jurassic Park",             "Action|Adventure|Sci-Fi", 3.92, 9_480),
            ("Titanic",                   "Drama|Romance",       3.85, 9_120),
            ("Home Alone",                "Children|Comedy",     3.72, 8_760),
        ],
    }
    rows = []
    for seg, films in pool.items():
        for rank, (title, genres, pred, n_users) in enumerate(films, 1):
            rows.append({
                "segment":              seg,
                "rank":                 rank,
                "title":                title,
                "genres":               genres,
                "avg_predicted_rating": pred,
                "recommended_to_users": n_users,
            })
    return pd.DataFrame(rows)
