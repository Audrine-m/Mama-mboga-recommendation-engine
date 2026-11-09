
from recommender import read_purchases, RecommendationEngine, DATA_PATH


def main():
    # 1. Read and validate purchase records
    valid_rows, rejected_rows = read_purchases(DATA_PATH)

    # 2. Initialise the recommendation engine
    engine = RecommendationEngine(valid_rows)

    # 3. Generate recommendations for all customers
    all_recommendations = engine.recommend_all(n=3)

    # 4. Export recommendations
    engine.export_csv(all_recommendations)

    # 5. Generate project summary
    report = engine.summary(
        purchases_read=len(valid_rows) + len(rejected_rows),
        purchases_used=len(valid_rows),
        purchases_rejected=len(rejected_rows),
        recommendations_written=len(all_recommendations)
    )

    # 6. Display results
    print("\nMAMA MBOGA ONLINE")
    print("========================")
    print("Recommendation Engine completed successfully.\n")

    print("PROJECT SUMMARY")
    print("========================")

    for key, value in report.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("\nOUTPUT")
    print("========================")
    print("Recommendations saved to: output/recommendations.csv")


if __name__ == "__main__":
    main()
