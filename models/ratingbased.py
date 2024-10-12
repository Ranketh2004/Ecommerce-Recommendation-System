import pandas as pd 

def rating_based_recommendations(data):
    average_ratings = data.groupby(['Name','ReviewCount','Brand','ImageURL'])['Rating'].mean().reset_index()
    
    top_rated_items = average_ratings.sort_values('Rating',ascending=False)
    rating_based_items = top_rated_items.head(12)

    rating_based_items.loc[:,'Rating'] = rating_based_items.loc[:,'Rating'].astype(int)
    rating_based_items.loc[:,'ReviewCount'] = rating_based_items.loc[:,'ReviewCount'].astype(int)
    
     # Function to get the first image URL
    def get_first_url(url):
        return url.split('|')[0] if pd.notna(url) else None
    
    ratingBasedItemDetails = rating_based_items[['Name', 'Rating', 'ReviewCount', 'Brand', 'ImageURL']]
    ratingBasedItemDetails['ImageURL'] = ratingBasedItemDetails['ImageURL'].apply(get_first_url)
    
    return ratingBasedItemDetails