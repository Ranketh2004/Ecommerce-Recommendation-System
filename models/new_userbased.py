# models/new_userbased.py

import pandas as pd

def new_user_recommendation(df, preferred_categories, preferred_brands, top=6):
    """
    Recommend products based on the preferred categories and brands for new users.

    :param df: DataFrame containing the product data.
    :param preferred_categories: List of categories selected by the user.
    :param preferred_brands: List of brands selected by the user.
    :param top: Number of products to recommend (default is 5).
    :return: DataFrame with the recommended products.
    """
    # Normalize categories and brands to lower case and strip whitespaces
    preferred_categories = [category.lower().strip() for category in preferred_categories]
    preferred_brands = [brand.lower().strip() for brand in preferred_brands]

    # Ensure the columns in the DataFrame are also normalized
    df['Category'] = df['Category'].str.lower().str.strip()
    df['Brand'] = df['Brand'].str.lower().str.strip()

    print(f"Preferred Categories: {preferred_categories}")  # Debug print
    print(f"Preferred Brands: {preferred_brands}")  # Debug print

    # Check if the required columns are present in the DataFrame
    if not all(col in df.columns for col in ['Category', 'Brand', 'Rating']):
        print("Error: Missing required columns in the data DataFrame.")
        return None

    # Filter products that match the user's preferred categories and brands
    filtered_df = df[(df['Category'].isin(preferred_categories)) & (df['Brand'].isin(preferred_brands))]
    print(f"Filtered products count (categories and brands): {len(filtered_df)}")  # Debug print

    # If there are not enough products, fall back to either categories or brands
    if len(filtered_df) < top:
        print("Not enough products found, falling back to categories or brands...")
        filtered_df = df[(df['Category'].isin(preferred_categories)) | (df['Brand'].isin(preferred_brands))]
        print(f"Filtered products count (either categories or brands): {len(filtered_df)}")  # Debug print

    # If no products found, show top-rated products as a fallback
    if len(filtered_df) == 0:
        print("No exact match found. Showing top-rated products as fallback...")
        filtered_df = df.sort_values(by='Rating', ascending=False).head(top)

    # Sort the filtered products based on Rating or any other metric
    filtered_df = filtered_df.sort_values(by='Rating', ascending=False)
    
     # Function to get the first image URL
    def get_first_url(url):
        return url.split('|')[0] if pd.notna(url) else None

    # Return top 'n' products
    recommended_items = filtered_df.head(top)
    recommended_items['ImageURL'] = recommended_items['ImageURL'].apply(get_first_url)
    
    print(f"Number of recommended items: {len(recommended_items)}")  # Debug print
    return recommended_items
