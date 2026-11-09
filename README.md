# Mama Mboga Online – Customer Recommendation Engine

A simple, explainable product recommendation system built with Python to help a small retail business make better use of its customer purchase history.

## About the Project

Imagine running a small grocery business where customers regularly purchase everyday essentials such as rice, cooking oil, flour and sugar. Over time, purchase records begin to reveal patterns: customers who buy certain products may also be interested in other products purchased by people with similar shopping habits.

I built this project around that idea.

**Mama Mboga Online** is a customer-based recommendation engine that analyses purchase history and suggests products a customer has not bought before. Rather than relying on a machine learning library or a black-box recommendation model, I implemented the core logic using Python's standard library.

My main objective was to understand how a recommendation system works behind the scenes, from reading and validating raw records to comparing customers, identifying relevant products, calculating recommendation scores and exporting the results.

## Project Objectives

The project focuses on:

- Reading and validating customer purchase records.
- Identifying products purchased by each customer.
- Measuring customer similarity using the Jaccard similarity coefficient.
- Finding customers with similar purchasing patterns.
- Identifying products that similar customers have purchased but the target customer has not.
- Ranking recommendations using an explainable scoring formula.
- Exporting recommendations into a structured CSV file.

## How It Works

The recommendation process follows a sequence of steps.

### 1. Data loading and validation

I used Python's built-in `csv` module to read the purchase dataset.

Before using the records, I implemented validation rules to handle common data quality issues:

- Missing required fields are rejected.
- Purchase quantities must be valid integers greater than zero.
- Duplicate purchase IDs are rejected.
- Customer, product and purchase IDs are normalised to uppercase.
- Rejected records are retained separately with reasons for rejection.

This ensures that invalid records do not enter the recommendation process.

### 2. Building customer purchase histories

For every customer, the engine creates a set of unique product IDs representing the products they have purchased.

It also builds lookup dictionaries for:

- Customer names.
- Product names.
- Product categories.
- Product popularity.

These structures are created during initialisation, allowing subsequent methods to work with the prepared data rather than repeatedly scanning the original purchase records.

Product popularity is based on the number of distinct customers who purchased a product, rather than the total quantity sold.

### 3. Measuring customer similarity

I used the **Jaccard similarity coefficient** to compare customer purchase histories.

The formula is:

\[
J(A,B)=\frac{|A\cap B|}{|A\cup B|}
\]

Where:

- \(A\) represents the products purchased by the first customer.
- \(B\) represents the products purchased by the second customer.
- The intersection represents products both customers purchased.
- The union represents all unique products purchased by either customer.

The resulting score ranges from 0 to 1.

A score of 1 indicates identical product histories, while 0 indicates no shared products. When both sets are empty, the implementation returns 0.

### 4. Finding similar customers

The engine compares a target customer with other customers and ranks them according to their Jaccard similarity scores.

It excludes the target customer from its own neighbour list and excludes customers with zero similarity.

The three highest-ranked eligible neighbours are used when generating recommendations. Ties are resolved consistently using customer IDs.

### 5. Generating candidate products

Once similar customers have been identified, the engine looks at the products they purchased.

Any product already purchased by the target customer is excluded.

For each remaining candidate, the engine records:

- The customers who purchased the product.
- The combined similarity scores of those supporting customers.
- The number of supporting customers.
- The product's overall popularity.

If no eligible similar customers are found, the engine falls back to products with the highest overall popularity, excluding products the customer has already purchased.

### 6. Ranking recommendations

I designed a weighted scoring formula that combines three signals:

| Scoring component | Weight |
|---|---:|
| Similarity strength | 60% |
| Neighbour support rate | 25% |
| Product popularity | 15% |

The formula is:

\[
Score = 0.60S + 0.25R + 0.15P
\]

Where:

- \(S\) is the sum of supporting neighbours' similarity scores divided by the total number of selected neighbours.
- \(R\) is the proportion of selected neighbours who purchased the candidate product.
- \(P\) is the product's popularity divided by the popularity of the most popular product.

The weights reflect my decision to give greater importance to similarity between customers while still considering how widely a product is purchased.

For customers who have no eligible neighbours, the engine uses normalised product popularity as the fallback score.

Recommendations are sorted from highest to lowest score, with product ID used to break ties consistently.

## Project Results

After running the complete workflow on the supplied purchase dataset, the engine produced the following results:

| Metric | Result |
|---|---:|
| Purchase records read | 63 |
| Valid records used | 60 |
| Rejected records | 3 |
| Unique customers processed | 20 |
| Unique products identified | 15 |
| Recommendation rows exported | 46 |

These results demonstrate the complete workflow, from raw purchase records to customer-level product recommendations.

## Project Structure

```text
   recommendation-engine/
│
├── data/
│   └── purchases.csv
│
├── output/
│   └── recommendations.csv
│
├── tests/
│
├── main.py
├── recommender.py
├── requirements.txt
└── README.md
```

## Technologies Used

- **Python 3** – Core programming language.
- **csv** – Reading purchase records and exporting recommendations.
- **pathlib** – Managing file paths and output directories.
- **Python sets and dictionaries** – Building customer histories, lookups and recommendation evidence.

The project uses Python's standard library and does not require external machine learning or data science packages.

## Testing

I used Python's built-in `unittest` framework to test the recommendation engine independently of the full purchase dataset.

The current test suite covers:

- Jaccard similarity calculations, including identical, disjoint and empty sets.
- Customer purchase history retrieval.
- Customer similarity calculations.
- Handling of unknown customer IDs.
- Exclusion of previously purchased products.
- Recommendation ranking.

To run the tests from the project root:

```bash
python -m unittest discover -s tests -v
```

All nine tests passed during development.

## Running the Project

### 1. Clone the repository

```bash
git clone https://github.com/Audrine-m/Mama-mboga-recommendation-engine.git
```

### 2. Navigate into the project directory

```bash
cd Recommendation Engine
```

### 3. Run the application

```bash
python main.py
```

The program reads the purchase dataset, validates records, builds customer histories, generates recommendations and exports the results.

### 4. View the output

The generated file is saved at:

```text
output/recommendations.csv
```

The CSV includes the customer ID and name, recommendation rank, product details, recommendation score and supporting customers.

## Design Decisions and Limitations

A few decisions shaped how I approached this project:

- I used Jaccard similarity because purchase histories can be represented naturally as sets of products.
- I used distinct-customer popularity rather than transaction quantity to avoid allowing repeated purchases by one customer to dominate the popularity measure.
- I kept the scoring formula transparent so that each recommendation can be explained.
- I included a popularity fallback so that customers without sufficiently similar neighbours can still receive suggestions.
- I used a fixed neighbourhood size of three for the recommendation workflow.

There are also limitations worth acknowledging. The recommendations are based on the available purchase history, so customers with very little history may receive less relevant suggestions. The system does not currently account for purchase recency, seasonal demand, product prices, stock availability or customer preferences beyond observed purchases.

These are areas I would consider when extending the project.

## What I Learned

Building this project helped me understand that recommendation systems are not necessarily dependent on complex machine learning algorithms. A useful recommendation workflow can begin with good data preparation, appropriate similarity measures and clearly defined ranking rules.

I also strengthened my understanding of Python classes, dictionaries, sets, data validation, exception handling, sorting and CSV file operations.

Most importantly, I learned to think about the reasoning behind a recommendation: not just which product is suggested, but why it is suggested and what evidence supports that decision.

## Future Improvements

Some improvements I would explore in a future version include:

- Incorporating purchase frequency and recency.
- Considering product co-occurrence and category preferences.
- Introducing configurable neighbourhood sizes and similarity thresholds.
- Adding automated unit tests for data validation and recommendation logic.
- Evaluating recommendation quality using historical purchase data.
- Developing a simple dashboard to explore customer recommendations and purchasing patterns.

---

**Project:** Mama Mboga Online – Customer Recommendation Engine  
**Language:** Python  
**Approach:** Customer-based collaborative filtering with popularity fallback  
**Implementation:** Python standard library