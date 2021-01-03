import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz
import warnings
warnings.filterwarnings("ignore")
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

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

def compare_score(unique_values, threshold):
    """
    Return a table that has unique values and their matches
    from fuzz.token_sort_ratio and fuzz.token_set_ratio
    """
    
    scorer = [fuzz.token_sort_ratio, fuzz.token_set_ratio]
    scorer_group = {}
    for s in range(len(scorer)):
        # Create tuples of brand names, matched brand names, and the score
        score = [(x,) + i
                 for x in unique_values
                 for i in process.extract(x, unique_values, scorer=scorer[s])]
        
        # Create dataframe from the tuples
        similarity = pd.DataFrame(score, columns=['value','match','score'])
        
        # Derive representative values
        similarity['sorted_value'] = np.minimum(similarity['value'], similarity['match'])
        high_score = similarity[(similarity['score'] >= threshold) &
                                (similarity['value'] != similarity['match']) &
                                (similarity['sorted_value'] != similarity['match'])]
        
        # Create columns with values combining scores
        high_score['scorer'] = high_score['value'] + ': ' + high_score['score'].astype(str)
        # Group data by matched values and store them in a new dataframe
        group = high_score.groupby(['match']).agg({'scorer': ', '.join}).reset_index()
        # Add to a dictionary
        scorer_group.update({'value' + str(s): group['match'].values,
                          'scorer' + str(s): group['scorer'].values})
    
    # Create tables from the dictionary
    token_sort = pd.DataFrame(index=scorer_group.get('value0'),
                              data=scorer_group.get('scorer0')).rename(columns={0:'token_sort_ratio'})
    token_set = pd.DataFrame(index=scorer_group.get('value1'),
                             data=scorer_group.get('scorer1')).rename(columns={0:'token_set_ratio'})
    # Outer join two tables by values
    similarity = token_sort.join(token_set, how='outer')
    # Replace NaN values and rename columns for readability
    similarity = similarity.replace(np.nan,'')
    return similarity
