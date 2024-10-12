from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from rapidfuzz import process, fuzz  # Correct import for rapidfuzz

def content_based_recommendation(df, item, top):
    """
    Recommend items similar to the given item using content-based filtering.
    
    :param df: DataFrame containing the product data.
    :param item: Name of the item to find similar products for.
    :param top: Number of similar products to return.
    :return: DataFrame of recommended items.
    """
    # Use fuzzy matching to find the closest matching product names
    # process.extract uses the scorer argument to apply fuzz.partial_ratio for matching
    matches = process.extract(item, df['Name'].values, scorer=fuzz.partial_ratio, limit=5)
    best_match_name = matches[0][0]  # Get the name of the best matching item

    print(f"Fuzzy matched item: {best_match_name} with score: {matches[0][1]}")  # Debug print

    # Check if the best match is good enough (e.g., score > 70)
    if matches[0][1] < 70:  # Adjust the score threshold as needed
        print("No good matches found.")
        return None

    # Get the index of the best matching item in the DataFrame
    item_index = df[df['Name'] == best_match_name].index[0]

    # Create TF-IDF for item descriptions (or any relevant feature like Tags)
    tfidf_vectorizer = TfidfVectorizer(stop_words="english")
    
    # Apply TF-IDF to the 'Tags' column
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['Tags'].fillna(''))
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")  # Debug print
    
    # Get cosine similarities of each item
    cosine_similarity_ofitems = cosine_similarity(tfidf_matrix)

    # Enumerate over cosine similarity values of the target item
    similar_items = list(enumerate(cosine_similarity_ofitems[item_index]))

    # Sort the items in descending order based on their similarity scores
    similar_items = sorted(similar_items, key=lambda x: x[1], reverse=True)
    
    # Select the required number of similar items
    top_similar_items = similar_items[1:top+1]  # Skip the first one as it is the same item

    # Get the indices of the recommended items
    recommended_items = [x[0] for x in top_similar_items]

    print(f"Number of recommended items: {len(recommended_items)}")  # Debug print

    # Function to get the first image URL
    def get_first_url(url):
        return url.split('|')[0] if pd.notna(url) else None

    # Return the recommended item details
    recommended_item_details = df.iloc[recommended_items][['Name', 'Brand', 'Rating', 'ImageURL']]
    recommended_item_details['ImageURL'] = df.iloc[recommended_items]['ImageURL'].apply(get_first_url)
    
    print(f"Recommended items:\n{recommended_item_details}")  # Debug print

    return recommended_item_details

    