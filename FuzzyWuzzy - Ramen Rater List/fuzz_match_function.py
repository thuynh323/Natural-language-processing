def fuzz_match(unique_list, scorer, threshold):
    score = [(x,) + i
             for x in unique_list
             for i in process.extract(x, unique_list, scorer=scorer)]
    
    similarity = pd.DataFrame(score, columns=['brand','match','score'])
    similarity['sorted_brand'] = np.minimum(similarity['brand'], similarity['match'])
    
    high_score = similarity[(similarity['score'] >= threshold) &
                            (similarity['brand'] != similarity['match']) &
                            (similarity['sorted_brand'] != similarity['match'])]
    high_score = high_score.drop('sorted_brand', axis=1)
    
    result = high_score.groupby(['brand','score']).agg(
                                {'match': ', '.join}).sort_values(
                                ['score'], ascending=False)
    return result
