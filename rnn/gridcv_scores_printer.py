'''
Influenced by https://gist.github.com/willwest/fcb61b110b9f7f59db40
'''

import csv
import numpy as np
from sklearn.model_selection import GridSearchCV


def save_gridcv_scores(gs_clf: GridSearchCV, export_file: str):
    '''Exports a CSV of the GridCV scores.
    gs_clf: A GridSearchCV object which has been fitted
    export_file: A file path
    Example output (file content):
    mean,std,feat__words__ngram_range,feat__words__stop_words,clf__alpha
    0.56805074971164937,0.0082019735998974941,"(1, 2)",english,0.0001
    0.57189542483660127,0.0066384723824170488,"(1, 2)",None,0.0001
    0.56839677047289505,0.0082404203511470264,"(1, 3)",english,0.0001
    0.57306164295783668,0.0095988722286300399,"(1, 3)",None,0.0001
    0.53524285531205951,0.0026015635012174854,"(1, 2)",english,0.001
    0.53742150454953219,0.0031141868512110649,"(1, 2)",None,0.001
    0.53510829168268614,0.0032487504805843725,"(1, 3)",english,0.001
    0.53717160066641034,0.0034025374855825019,"(1, 3)",None,0.001
    '''
    with open(export_file, 'w', newline='') as outfile:
        csvwriter = csv.writer(outfile, delimiter=',')

        # Create the header using the parameter names
        header = ["rank", "mean", "std"]

        results = gs_clf.cv_results_
        params = results['params']

        param_names = params[0].keys()
        header.extend(param_names)

        csvwriter.writerow(header)

        rows = []
        for idx, param in enumerate(params):
            # Get mean and standard deviation
            rank = results['rank_test_score'][idx]
            mean = results['mean_test_score'][idx]
            std = results['std_test_score'][idx]
            row = [rank, mean, std]

            # Get the list of parameter settings and add to row
            params = [str(p) for p in param.values()]
            row.extend(params)
            rows.append(row)

        rows = np.array(rows)
        ind = np.argsort(rows[:,0]); rows = rows[ind]  # Order by ranking

        csvwriter.writerows(rows)
