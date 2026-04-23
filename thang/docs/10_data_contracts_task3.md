# 10. Data Contracts - Task 3 Outputs

Tai lieu nay chot schema dau ra cho Task 3 de Task 4 (BI) co the ket noi on dinh.

## movies_enriched

- movieId: int
- title: string
- title_clean: string
- year: int
- decade: int
- genres: string
- genres_array: array<string>
- avg_rating: double
- rating_count: long
- rating_stddev: double
- imdbId: string
- tmdbId: string
- revenue: double
- budget: double
- roi: double

## genre_stats

- genre: string
- avg_rating: double
- rating_count: long
- movie_count: long
- total_revenue: double
- avg_revenue: double
- avg_budget: double
- avg_roi: double

## decade_stats

- decade: int
- genre: string
- avg_rating: double
- rating_count: long
- avg_revenue: double
- movie_count: long

## year_stats

- rating_year: int
- rating_count: long
- avg_rating: double
- active_users: long

## rating_dist

- rating: double
- frequency: long

## user_segments

- userId: int
- segment: string
- rating_count: long
- avg_rating: double
- unique_movies_rated: long

## segment_genre_preference

- segment: string
- genre: string
- rating_count: long
- avg_rating: double
- genre_rank: int

## tag_stats

- tag: string
- frequency: long

## segment_recommendations

- segment: string
- movieId: int
- avg_predicted_rating: double
- recommended_to_users: long
- rank: int
- title_clean: string
- genres_array: array<string>
- avg_rating: double
