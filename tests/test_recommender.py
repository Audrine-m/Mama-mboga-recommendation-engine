
import unittest

from recommender import RecommendationEngine, jaccard


class TestRecommendationEngine(unittest.TestCase):

    def setUp(self):
        # Small dataset with predictable purchase patterns
        self.purchases = [
            {
                "customer_id": "C101",
                "customer_name": "Mary",
                "product_id": "P01",
                "product_name": "Rice",
                "category": "Grains"
            },
            {
                "customer_id": "C101",
                "customer_name": "Mary",
                "product_id": "P02",
                "product_name": "Cooking Oil",
                "category": "Cooking"
            },
            {
                "customer_id": "C102",
                "customer_name": "John",
                "product_id": "P01",
                "product_name": "Rice",
                "category": "Grains"
            },
            {
                "customer_id": "C102",
                "customer_name": "John",
                "product_id": "P02",
                "product_name": "Cooking Oil",
                "category": "Cooking"
            },
            {
                "customer_id": "C102",
                "customer_name": "John",
                "product_id": "P03",
                "product_name": "Sugar",
                "category": "Groceries"
            },
            {
                "customer_id": "C103",
                "customer_name": "Jane",
                "product_id": "P04",
                "product_name": "Milk",
                "category": "Dairy"
            }
        ]

        self.engine = RecommendationEngine(self.purchases)

    def test_jaccard_similarity(self):
        result = jaccard({"A", "B"}, {"B", "C"})
        self.assertAlmostEqual(result, 1 / 3)

    def test_identical_sets(self):
        result = jaccard({"A", "B"}, {"A", "B"})
        self.assertEqual(result, 1.0)

    def test_disjoint_sets(self):
        result = jaccard({"A"}, {"B"})
        self.assertEqual(result, 0.0)

    def test_empty_sets(self):
        result = jaccard(set(), set())
        self.assertEqual(result, 0.0)

    def test_customer_history(self):
        result = self.engine.history("C101")
        self.assertEqual(result, {"P01", "P02"})

    def test_customer_similarity(self):
        result = self.engine.similarity("C101", "C102")
        self.assertAlmostEqual(result, 2 / 3)

    def test_unknown_customer(self):
        with self.assertRaises(KeyError):
            self.engine.history("C999")

    def test_recommendations_exclude_purchased_products(self):
        recommendations = self.engine.recommend("C101", n=3)

        recommended_ids = {
            item["product_id"] for item in recommendations
        }

        self.assertNotIn("P01", recommended_ids)
        self.assertNotIn("P02", recommended_ids)

    def test_recommendations_are_ranked(self):
        recommendations = self.engine.recommend("C101", n=3)

        scores = [item["score"] for item in recommendations]

        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
