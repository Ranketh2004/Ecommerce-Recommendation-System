import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def userbased_recommendation(df, target_user, top):
    # Create user-item matrix where rows are users, columns are product IDs, and the values are ratings
    user_item_matrix = df.pivot_table(index='ID', columns='ProdID', values='Rating', aggfunc='mean').fillna(0).astype(int)
    
    # Calculate cosine similarity between each user
    user_similarities_matrix = cosine_similarity(user_item_matrix)
    
    # Get the index of the target user
    target_user_index = user_item_matrix.index.get_loc(target_user)
    
    # Get the similarity score of the target user with other users
    similarity_of_user = user_similarities_matrix[target_user_index]
    
    # Sort the similarities in descending order excluding index 0
    similar_user_indices = similarity_of_user.argsort()[::-1][1:]

    # Create a list to add recommended items
    recommend_items = []
    
    for user_index in similar_user_indices:
        # Get the product ratings of similar users
        rated_by_similar_user = user_item_matrix.iloc[user_index]
        
        # Find products that similar user has rated but the target user has not
        not_rated_by_target_user = (rated_by_similar_user == 0) & (user_item_matrix.iloc[target_user_index] == 0)
        
        # Add up to 5 products per similar user
        recommend_items.extend(user_item_matrix.columns[not_rated_by_target_user][:5])
    
    # Remove duplicated recommendations
    recommend_items = list(set(recommend_items))
    
    # Function to get the first image URL
    def get_first_url(url):
        return url.split('|')[0] if pd.notna(url) else None
    
    # Select the required columns to output
    recommended_item_details = df[df['ProdID'].isin(recommend_items)][['Name', 'Brand', 'Rating', 'ImageURL']][:top+1]
    
    # Apply the get_first_url function to the ImageURL column
    recommended_item_details['ImageURL'] = recommended_item_details['ImageURL'].apply(get_first_url)
    
    return recommended_item_details
