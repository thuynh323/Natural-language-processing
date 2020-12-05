import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz

ramen = pd.read_excel('The-Ramen-Rater-The-Big-List-1-3400-Current-As-Of-Jan-25-2020.xlsx')

# Get a list of unique values
unique_brand = ramen['Brand'].unique().tolist()

def get_score(scorer, threshold):
	"""
	Return a table of each brand name, its corresponding
	similar names found in the list, and their score

	Parameters:
	scorer - the selected scorer (fuzz.token_sort_ratio, fuzz.token_set_ratio)
	threshold - the cut-off score
	"""

    # Create tuples of brand names, matched brand names, and the score
    score = [(x,) + i
             for x in unique_brand
             for i in process.extract(x, unique_brand, scorer=scorer)]
    
    # Create dataframe from the tuples
    similarity = pd.DataFrame(score, columns=['brand','match','score'])
    
    # Derive representative values
    similarity['sorted_brand'] = np.minimum(similarity['brand'], similarity['match'])
    high_score = similarity[(similarity['score'] >= threshold) &
                            (similarity['brand'] != similarity['match']) &
                            (similarity['sorted_brand'] != similarity['match'])]

    # Group matches by brand names and scores
    result = high_score.groupby(['brand','score']).agg({'match': ', '.join}).sort_values(['score'], ascending=False)
    return result
