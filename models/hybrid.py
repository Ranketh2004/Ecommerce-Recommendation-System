import pandas as pd
from models.content_based import content_based_recommendation
from models.userbased import userbased_recommendation

#combine userbased and content based
def hybrid_recommendation(df,user,item,top):
    content_based = content_based_recommendation(df,item,top)
    user_based = userbased_recommendation(df,user,top)

    #concatanate both recommendations and remove duplicates
    hybrid_recom = pd.concat([content_based,user_based]).drop_duplicates()
    return hybrid_recom.head(top)
