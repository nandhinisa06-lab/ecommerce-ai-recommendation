import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load products
products = pd.read_csv("products.csv")


# Combine category and description
products["features"] = (
    products["category"] + " " + products["description"]
)


# Convert text into TF-IDF features
vectorizer = TfidfVectorizer()

feature_matrix = vectorizer.fit_transform(
    products["features"]
)


# Calculate similarity
similarity = cosine_similarity(feature_matrix)


# Recommendation function
def recommend_products(
    product_id,
    number_of_recommendations=3
):

    # Find selected product
    index = products[
        products["id"] == product_id
    ].index[0]


    # Get similarity scores
    similarity_scores = list(
        enumerate(similarity[index])
    )


    # Sort by similarity
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )


    # Store recommendations
    recommended_products = []


    # Get top recommendations
    for i, score in similarity_scores[
        1:number_of_recommendations + 1
    ]:

        recommended_products.append({

            "id": int(
                products.iloc[i]["id"]
            ),

            "name": products.iloc[i]["name"],

            "reason":
                "Similar category and product features"
        })


    return recommended_products