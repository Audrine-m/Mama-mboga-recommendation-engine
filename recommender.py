import csv
from pathlib import Path

DATA_PATH = Path("data") / "purchases.csv"
OUTPUT_PATH = Path("output") / "recommendations.csv"


def read_purchases(path: Path = DATA_PATH) -> tuple[list[dict], list[dict]]:
    """
    Read purchase records from a CSV file.

    Returns:
        valid_rows: Records that pass validation.
        rejected_rows: Records that fail validation, with reasons.
    """

    valid_rows = []
    rejected_rows = []
    seen_purchase_ids = set()

    with open(path, mode="r", newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Clean text fields by removing surrounding spaces
            row = {
                key: value.strip() if value else ""
                for key, value in row.items()
            }

            # Standardize IDs
            row["purchase_id"] = row["purchase_id"].upper()
            row["customer_id"] = row["customer_id"].upper()
            row["product_id"] = row["product_id"].upper()

            # Check required fields
            required_fields = [
                "purchase_id",
                "customer_id",
                "customer_name",
                "product_id",
                "product_name",
                "category",
                "purchase_date"
            ]

            missing_fields = [
                field for field in required_fields if not row[field]
            ]

            if missing_fields:
                row["rejection_reason"] = (
                    f"Missing fields: {', '.join(missing_fields)}"
                )
                rejected_rows.append(row)
                continue

            # Validate quantity
            try:
                quantity = int(row["quantity"])
            except ValueError:
                row["rejection_reason"] = "Quantity must be an integer"
                rejected_rows.append(row)
                continue

            if quantity <= 0:
                row["rejection_reason"] = "Quantity must be greater than zero"
                rejected_rows.append(row)
                continue

            row["quantity"] = quantity

            # Check duplicate transaction IDs
            if row["purchase_id"] in seen_purchase_ids:
                row["rejection_reason"] = "Duplicate purchase ID"
                rejected_rows.append(row)
                continue

            # Record the accepted transaction ID
            seen_purchase_ids.add(row["purchase_id"])

            valid_rows.append(row)

    return valid_rows, rejected_rows



def jaccard(a: set, b: set) -> float:
    """
    Calculate Jaccard similarity between two sets.

    Returns the ratio of shared elements
    to all unique elements.
    """

    # Find the shared elements
    intersection = a & b

    # Find all unique elements across both sets
    union = a | b

    # Handle two empty sets
    if not union:
        return 0.0

    # Calculate similarity
    return len(intersection) / len(union)



class RecommendationEngine:
    """Recommends products based on similar customers."""

    def __init__(self, purchases: list[dict], min_similarity: float = 0.0):

        self.min_similarity = min_similarity

        # Customer ID -> set of purchased product IDs
        self.customer_products = {}

        # Customer ID -> customer name
        self.customer_names = {}

        # Product ID -> product name
        self.product_names = {}

        # Product ID -> product category
        self.product_categories = {}

        # Product ID -> number of distinct customers who bought it
        self.product_popularity = {}

        # Build our data structures from the purchase records
        for row in purchases:

            customer_id = row["customer_id"]
            product_id = row["product_id"]

            # Create a set for each new customer
            self.customer_products.setdefault(customer_id, set())

            # Add the purchased product to the customer's history
            self.customer_products[customer_id].add(product_id)

            # Store customer information
            self.customer_names[customer_id] = row["customer_name"]

            # Store product information
            self.product_names[product_id] = row["product_name"]
            self.product_categories[product_id] = row["category"]

        # Calculate popularity using distinct customer histories
        for customer_id, products in self.customer_products.items():

            for product_id in products:

                self.product_popularity[product_id] = (
                    self.product_popularity.get(product_id, 0) + 1
                )



    def history(self, customer_id: str) -> set[str]:
        """Return the products purchased by a customer."""

        if customer_id not in self.customer_products:
            raise KeyError(f"Unknown customer ID: {customer_id}")

        return self.customer_products[customer_id]


    
    def similarity(self, customer_a: str, customer_b: str) -> float:
        """Calculate similarity between two customers."""

        history_a = self.history(customer_a)
        history_b = self.history(customer_b)

        return jaccard(history_a, history_b)



    def similar_customers(
        self, customer_id: str, k: int = 3
    ) -> list[tuple[str, float]]:
        """
        Return the top-k most similar customers.

        The target customer is excluded.
        Customers with zero similarity are excluded.
        Ties are broken alphabetically by customer ID.
        """

        # Validate the target customer
        if customer_id not in self.customer_products:
            raise KeyError(f"Unknown customer ID: {customer_id}")

        if k <= 0:
            return []

        similarities = []

        # Compare the target customer with every other customer
        for other_customer in self.customer_products:

            # Exclude the target customer
            if other_customer == customer_id:
                continue

            # Calculate similarity
            score = self.similarity(customer_id, other_customer)

            # Keep customers meeting the similarity threshold
            if score > 0 and score >= self.min_similarity:
                similarities.append((other_customer, score))

        # Sort by similarity (highest first), then customer ID
        ranked_customers = sorted(
            similarities,
            key=lambda x: (-x[1], x[0])
        )

        # Return only the top k customers
        return ranked_customers[:k]


    def candidate_products(
        self, customer_id: str, k: int = 3
    ) -> dict[str, dict]:
        """
        Find products purchased by similar customers
        that the target customer has not purchased.
        """

        # Validate customer
        if customer_id not in self.customer_products:
            raise KeyError(f"Unknown customer ID: {customer_id}")

        # Get the target customer's purchase history
        purchased_products = self.history(customer_id)

        # Find the nearest neighbours
        neighbours = self.similar_customers(customer_id, k)

        candidates = {}

        # Collect products purchased by neighbours
        for neighbour_id, similarity_score in neighbours:

            neighbour_products = self.history(neighbour_id)

            for product_id in neighbour_products:

                # Exclude products already purchased by the target customer
                if product_id in purchased_products:
                    continue

                # Create evidence for a new candidate product
                if product_id not in candidates:
                    candidates[product_id] = {
                        "supporters": [],
                        "similarity_sum": 0.0,
                        "support_count": 0,
                        "popularity": self.product_popularity[product_id],
                        "neighbour_count": len(neighbours)
                    }

                # Record which neighbour supports this product
                candidates[product_id]["supporters"].append(
                    (neighbour_id, similarity_score)
                )

                candidates[product_id]["similarity_sum"] += similarity_score

                candidates[product_id]["support_count"] += 1

        # Fallback: use popular products if no neighbours are available
        if not neighbours:

            for product_id, popularity in self.product_popularity.items():

                if product_id not in purchased_products:

                    candidates[product_id] = {
                        "supporters": [],
                        "similarity_sum": 0.0,
                        "support_count": 0,
                        "popularity": popularity,
                        "fallback": True,
                        "neighbour_count": 0
                    }

        return candidates



    def score(self, evidence: dict) -> float:
        max_popularity = max(self.product_popularity.values(), default=1)

        popularity_component = (
            evidence["popularity"] / max_popularity
        )

        # If there are no similar customers, use popularity alone.
        if evidence.get("fallback"):
            return popularity_component

        neighbour_count = evidence["neighbour_count"]

        similarity_component = (
            evidence["similarity_sum"] / neighbour_count
        )

        support_component = (
            evidence["support_count"] / neighbour_count
        )

        final_score = (
            0.60 * similarity_component
            + 0.25 * support_component
            + 0.15 * popularity_component
        )

        return final_score


    
    def recommend(self, customer_id: str, n: int = 3) -> list[dict]:
        if customer_id not in self.customer_products:
            raise KeyError(f"Unknown customer ID: {customer_id}")

        if n <= 0:
            return []

        candidates = self.candidate_products(customer_id, k=3)

        recommendations = []

        for product_id, evidence in candidates.items():
            product_score = self.score(evidence)

            supporters = [
                customer_id
                for customer_id, similarity in evidence["supporters"]
            ]

            recommendation = {
                "customer_id": customer_id,
                "customer_name": self.customer_names[customer_id],
                "product_id": product_id,
                "product_name": self.product_names[product_id],
                "category": self.product_categories[product_id],
                "score": product_score,
                "supporting_customers": supporters,
                "support_count": evidence["support_count"]
            }

            recommendations.append(recommendation)

        recommendations.sort(
            key=lambda item: (-item["score"], item["product_id"])
        )

        return recommendations[:n]



    def recommend_all(self, n: int = 3) -> list[dict]:
        all_recommendations = []

        for customer_id in self.customer_products:
            customer_recommendations = self.recommend(
                customer_id,
                n=n
            )

            if customer_recommendations:
                all_recommendations.extend(customer_recommendations)
            else:
                all_recommendations.append({
                    "customer_id": customer_id,
                    "customer_name": self.customer_names[customer_id],
                    "product_id": "",
                    "product_name": "",
                    "category": "",
                    "score": 0.0,
                    "supporting_customers": [],
                    "support_count": 0
                })

        return all_recommendations



    def export_csv(self, rows: list[dict], path: Path = OUTPUT_PATH) -> None:
        fieldnames = [
            "customer_id",
            "customer_name",
            "rank",
            "product_id",
            "product_name",
            "category",
            "score",
            "supporting_customers"
        ]

        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()

            customer_ranks = {}

            for row in rows:
                customer_id = row["customer_id"]

                customer_ranks[customer_id] = (
                    customer_ranks.get(customer_id, 0) + 1
                )

                writer.writerow({
                    "customer_id": customer_id,
                    "customer_name": row["customer_name"],
                    "rank": customer_ranks[customer_id],
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "category": row["category"],
                    "score": round(row["score"], 4),
                    "supporting_customers": "; ".join(
                        row["supporting_customers"]
                    )
                })

    
    def summary(
        self,
        purchases_read: int,
        purchases_used: int,
        purchases_rejected: int,
        recommendations_written: int
    ) -> dict:

        return {
            "purchases_read": purchases_read,
            "purchases_used": purchases_used,
            "purchases_rejected": purchases_rejected,
            "customers_processed": len(self.customer_products),
            "products_identified": len(self.product_names),
            "recommendations_written": recommendations_written
        }
