import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz

def get_score(unique_values, scorer, threshold):
    """
    Return a table of each brand name, its corresponding
    similar names found in the list, and their score
    Parameters:
    unique_value - the list of unique values
    scorer - the selected scorer (fuzz.token_sort_ratio, fuzz.token_set_ratio)
    threshold - the cut-off score
    """
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    
    # Create tuples of brand names, matched brand names, and the score
    score = [(x,) + i
             for x in unique_values
             for i in process.extract(x, unique_values, scorer=scorer)]
    
    # Create dataframe from the tuples
    similarity = pd.DataFrame(score, columns=['value','match','score'])
    
    # Derive representative values
    similarity['sorted_value'] = np.minimum(similarity['value'], similarity['match'])
    high_score = similarity[(similarity['score'] >= threshold) &
                            (similarity['value'] != similarity['match']) &
                            (similarity['sorted_value'] != similarity['match'])]

    # Group matches by brand names and scores
    if scorer == fuzz.token_sort_ratio:
        result = high_score.groupby(['value','score']).agg({'match': ', '.join}).sort_values(['score'], ascending=False)
    if scorer == fuzz.token_set_ratio:
        result = high_score.groupby(['match','score']).agg({'value': ', '.join}).sort_values(['score'], ascending=False)
    return result
