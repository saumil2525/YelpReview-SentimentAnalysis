from sklearn.tree import ExtraTreeClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.preprocessing import StandardScaler, MaxAbsScaler, MinMaxScaler, RobustScaler
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, NuSVC, LinearSVC
from sklearn.ensemble import (RandomForestClassifier, ExtraTreesClassifier, AdaBoostClassifier,
                              BaggingClassifier, GradientBoostingClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neighbors import (KNeighborsClassifier)
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline, make_union, Pipeline, FeatureUnion
from sklearn.metrics import (confusion_matrix, classification_report, accuracy_score, auc,
                             roc_auc_score, f1_score, precision_recall_curve, precision_score,
                             recall_score, roc_curve, r2_score, log_loss)
from sklearn.model_selection import (train_test_split, cross_val_score, GridSearchCV, KFold,
                                     StratifiedKFold, ShuffleSplit, StratifiedShuffleSplit,
                                     RandomizedSearchCV, validation_curve, learning_curve)
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from wordcloud import WordCloud
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
import re
import os
import sys
import operator

print(sys.executable)
print(sys.path)


def get_cleaned_text(review, words_len=3, remove_stopwords=False,
                     is_stemming=False, is_lemma=False, split=False):
    """Clean dataset

    Args:
        words_len (int, optional): [description]. Defaults to 3.
        remove_stopwords (bool, optional): [description]. Defaults to False.
        is_stemming (bool, optional): [description]. Defaults to False.
        is_lemma (bool, optional): [description]. Defaults to False.
        split (bool, optional): [description]. Defaults to False.

    Returns:
        [type]: [description]
    """
    review_text = re.sub("[^a-zA-Z]", " ", review)
    words = review_text.split()
    words = [w.lower() for w in words if len(w) >= words_len]
    if remove_stopwords:
        stop_words = set(stopwords.words("english"))
        # stop_words = stop_words.union(set('movi', 'film'))
        words = [w for w in words if not w in stop_words]
    if is_stemming:
        ps = PorterStemmer()
        words = [ps.stem(j) for j in words]
    if is_lemma:
        word_lemm = WordNetLemmatizer()
        pos = ['v', 'n', 'a']
        for p in pos:
            words = [word_lemm.lemmatize(k, pos=p) for k in words]
    if split:
        return words
    else:
        return (' '.join(words))


def clf_model(X_train, y_train, X_validation, y_validation, model=None, path4plot=None):
    """[summary]

    Args:
        X_train (array): Train data
        y_train (array): Train label
        X_validation (array): Test data
        y_validation (array): Test label
        model (str, optional): Classifier . Defaults to None.
        path4plot (str, optional): Path for storing images. Defaults to None.

    Returns:
       df_r (DataFrame): Dataframe with accuracy of classifier
       cm (list): List of confusion metrics for all the classifier
    """

    clfs_dict = {
        'KNearestNeighbour': KNeighborsClassifier(),
        'GaussianNaiveBayes': GaussianNB(),
        'MultinomialNaiveBayes': MultinomialNB(),
        'DecisionTree': DecisionTreeClassifier(),
        'RandomForest': RandomForestClassifier(),
        'ExtraTree': ExtraTreesClassifier(),
        'SupportVectorMachine': SVC(),
        'LogisticRegression': LogisticRegression(),
        'XGBoost': XGBClassifier(),
        'AdaptiveBoost': AdaBoostClassifier(),
        'Nu-SupportVector': NuSVC(),
        'LinearSupportVecor': LinearSVC(),
        'StochasticGradientBoost': SGDClassifier(),
        'GaussianProcessClassifier': GaussianProcessClassifier(),
        'BaggingClassifier': BaggingClassifier(KNeighborsClassifier(), ),
        'GradientBoostingClassifier': GradientBoostingClassifier(),
        # 'MultiLayerPerceptron': MLPClassifier(hidden_layer_sizes=(100, 100, 100), alpha=1e-5, solver='lbfgs', max_iter=500, ),
        'LightGradientBoost': LGBMClassifier()
    }
    if model is not None:
        clf = clfs_dict[model]
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_validation)
        train_acc = clf.score(X_train, y_train)
        test_acc = clf.score(X_validation, y_validation)

        print('Training Accuracy: ', train_acc)
        print('Test Accuracy: ', test_acc)
        cm = confusion_matrix(y_validation, y_pred)
        return None
    else:
        results = []
        cm = []
        for idx, model in enumerate(clfs_dict):
            try:
                print('\t {}. --> {}'.format((idx+1), model))
                clf = clfs_dict[model]
                clf.fit(X_train, y_train)
                y_pred = clf.predict(X_validation)
                train_acc = clf.score(X_train, y_train)
                test_acc = clf.score(X_validation, y_validation)
                f1_score_wighted = f1_score(
                    y_validation, y_pred, average='weighted')
                f1_score_micro = f1_score(
                    y_validation, y_pred, average='micro')
                f1_score_macro = f1_score(
                    y_validation, y_pred, average='macro')
                results.append(
                    [model, train_acc, test_acc, f1_score_wighted, f1_score_micro, f1_score_macro])
                cm.append([model, confusion_matrix(y_validation, y_pred)])
            except Exception as e:
                print('\t\t** error in ''{}'': {}'.format(model, str(e)))
                pass

        df_r = pd.DataFrame(
            results, columns=['classifier', 'train_acc', 'test_acc', 'f1_wighted', 'f1_macro', 'f1_macro'])
        # df_r.append([model, train_acc, test_acc])
        return df_r, cm


print('\nFinished Modeling.................')


def classifier_eval(clf, X_train, X_test, y_train, y_test, y_pred_train, avg='weighted'):
    """ 
    Evaluate performance calculate
        - calculate Train accuarcy
        - calculate Test accuracy
        - F1 score 
        - Area under curve
        - print classification report

    Args:
        clf (str): Select
        X_train (array): Train data
        X_test (array): Test data
        y_train (array): Train labels
        y_test (array): Test labels
        y_pred_train (array): Predicted Train Labels
        avg (str, optional): Average type for F1 scoring. Defaults to 'weighted'.
    """
    y_pred_train = clf.predict(X_train)
    y_pred = clf.predict(X_test)

    test_acc = accuracy_score(y_true=y_test, y_pred=y_pred)
    train_acc = accuracy_score(y_true=y_train, y_pred=y_pred_train)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_micro = f1_score(y_test, y_pred, average='micro')
    f1_weighted = f1_score(y_test, y_pred, average='weighted')
    # precision = precision_score(y_test, y_pred)
    # area_under_curve = auc(X_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True)
    fpr, tpr, _ = roc_curve(y_test, y_pred)
    area_under_curve = auc(fpr, tpr)
    plt.plot(fpr, tpr, color='darkorange',
             lw=2, label='ROC curve (area = %0.2f)' % area_under_curve)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.grid()
    print('AreaUnderCurve: ', area_under_curve)
    print('Test accuracy: ', test_acc)
    print('Train accuracy: ', train_acc)
    print('Test f1_micro: ', f1_micro)
    print('Test f1_macro: ', f1_macro)
    print('Test f1_weighted: ', f1_weighted)
    print(classification_report(y_test, y_pred))
