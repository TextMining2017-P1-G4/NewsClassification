import jieba
import numpy
import pandas

from sklearn.datasets import load_files
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from sklearn.linear_model import SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

from sklearn import metrics


def jieba_cut(s):
    return list(jieba.cut(s))



if __name__ == '__main__':
    
    import os
    import sys
    import getopt
    
    def usage():
        print('    Usage:')
        print('        -T    Folder name for training news.')
        print('        -E    Folder name for testing news.')
    

    if len(sys.argv) <= 1:
        print('{} -h'.format(sys.argv[0]))
        usage()
        sys.exit(2)
        
    
    try:
        opt_list, args = getopt.getopt(sys.argv[1:], 'T:E:')
    except (getopt.GetoptError, msg):
        print('{} -h'.format(sys.argv[0]))
        usage()
        sys.exit(2)
        
        
    for o, a in opt_list:
        if o in ('-T'):
            train_data_folder = a
        if o in ('-E'):
            test_data_folder = a


    
    # SVM training
    training_data = load_files(train_data_folder, shuffle=False, encoding='utf-8')
    x_train, _, y_train, _ = train_test_split(training_data.data, training_data.target, test_size=0.0000001)
    
    pipeline = Pipeline([
        ('vect', TfidfVectorizer(binary=True, tokenizer=jieba_cut)),
        ('clf', SVC()),
    ])
    # pipeline.get_params().keys()
    # GridSearchCV
    parameters = {
        
        # TfidfVectorizer
        'vect__use_idf': [True, False],
        'vect__min_df': numpy.linspace(0, 0.5, 2, endpoint=False),
        'vect__max_df': numpy.linspace(0.5, 1, 3),
        'vect__ngram_range': [(1,1), (1,2), (2,2)],
        
        # Support Vector Classifier
        'clf__C': numpy.logspace(-1, 1, 3),
        'clf__kernel': ['linear', 'poly', 'rbf'],# 'sigmoid', 'precomputed'],
        'clf__gamma': numpy.logspace(-1, 1, 3),
    }
    gs_clf = GridSearchCV(pipeline, param_grid=parameters, n_jobs=-1)
    gs_clf.fit(x_train, y_train)
    
    
    
    # SVM testing
    testing_data = load_files(test_data_folder, encoding='utf-8')
    _, x_test, _, y_test = train_test_split(testing_data.data, testing_data.target, train_size=0.0000001)
    #pred = gs_clf.predict(x_test)
    pred = gs_clf.best_estimator_.predict(x_test)
    
    
    
    # SVM parameters summary report
    #gs_clf.cv_results_.keys()
    gs_clf_params = list(gs_clf.cv_results_['params'])
    mean_test_scores = list(gs_clf.cv_results_['mean_test_score'])
    rank_test_score = list(gs_clf.cv_results_['rank_test_score'])
    
    gs_clf_summary = \
        [dict(list(d.items()) + [('mean_test_score', m), ('rank_test_score', r)])
        for d, m, r in zip(gs_clf_params, mean_test_scores, rank_test_score)]
        
    gs_clf_summary = \
        sorted(gs_clf_summary, key=lambda d: d['rank_test_score'], reverse=False)
        
    columns = ['rank_test_score',
               'mean_test_score',
               'vect__use_idf',
               'vect__min_df',
               'vect__max_df',
               'vect__ngram_range',
               'clf__kernel',
               'clf__C',
               'clf__gamma']
    gs_clf_summary_df = pandas.DataFrame(gs_clf_summary, columns=columns)
    data_file = 'parameters_summary.xlsx'
    writer = pandas.ExcelWriter(data_file, engine='xlsxwriter')
    gs_clf_summary_df.to_excel(writer, sheet_name='summary', index=False)
    writer.save()
    
    
    with open('prediction_summary.txt', 'w') as f:
        f.write(metrics.classification_report(y_test, pred,
                target_names=testing_data.target_names))