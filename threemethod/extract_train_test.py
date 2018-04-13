#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 13:09:08 2018

@author: hans
"""

import cv2
import os
import numpy as np
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import AdaBoostClassifier
from skimage import transform
from sklearn import tree
import datetime

mode = 0
if mode == 0:
    filename = '_feature_gray.pkl'
elif mode == 1:
    filename = '_feature_rgb.pkl'

train_list = "images/train.txt"
test_list = "images/test.txt"


# train_list = "train.txt"
# test_list = "train.txt"
def gray(img_path):
    img = cv2.imread(img_path, 0)
    img = transform.resize(img, (227, 227))
    # img = img.resize((227,227))
    img = img * 255
    img = img.astype(np.uint8)
    feature = cv2.calcHist([img], [0], None, [256], [0, 256]).reshape(1, -1)
    return feature


def rgb(img_path):
    img = cv2.imread(img_path)
    img = transform.resize(img, (227, 227, 3))
    b = img[:, :, 0] * 255
    g = img[:, :, 1] * 255
    r = img[:, :, 2] * 255
    b = b.astype(np.uint8)
    g = g.astype(np.uint8)
    r = r.astype(np.uint8)
    feature_b = cv2.calcHist([b], [0], None, [256], [0, 256]).reshape(1, -1)
    feature_g = cv2.calcHist([g], [0], None, [256], [0, 256]).reshape(1, -1)
    feature_r = cv2.calcHist([r], [0], None, [256], [0, 256]).reshape(1, -1)
    feature = np.hstack((feature_b, feature_g, feature_r))
    return feature


def hist_feature(list_txt):
    root_path = 'images/train/'
    with open(list_txt, 'r') as f:
        line = f.readline()
        img_path = os.path.join(root_path, line.split(' ')[0])
        if mode == 0:
            feature = gray(img_path)
        elif mode == 1:
            feature = rgb(img_path)
        label = np.array([int(line.split(' ')[1].split('\n')[0])])
        line = f.readline()
        num = 2
        while line:
            img_path = os.path.join(root_path, line.split(' ')[0])
            if not os.path.isfile(img_path):
                line = f.readline()
                continue
            print("%d dealing with %s ..." % (num, line.split(' ')[0]))
            if mode == 0:
                hist_cv = gray(img_path)
            elif mode == 1:
                hist_cv = rgb(img_path)
            feature = np.vstack((feature, hist_cv))
            label = np.hstack((label, np.array([int(line.split(' ')[1].split('\n')[0])])))
            num += 1
            line = f.readline()
    joblib.dump(feature, list_txt.split('.')[0] + filename, compress=5)
    joblib.dump(label, list_txt.split('.')[0] + '_label.pkl', compress=5)
    return feature, label


def save_feature():
    t1 = datetime.datetime.now()
    # X_train, y_train = hist_feature(train_list)
    t2 = datetime.datetime.now()
    X_test, y_test = hist_feature(test_list)
    t3 = datetime.datetime.now()
    print("\ntime of extracting train features: %0.2f" % (t2 - t1).total_seconds())
    print("time of extracting test features: %0.2f" % (t3 - t2).total_seconds())


def decision_tree():
    dt = tree.DecisionTreeClassifier(criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1,
                                     random_state=80)
    return fit(dt, 'dt')


def random_forest():
    # criterion: 分支的标准(gini/entropy), n_estimators: 树的数量, bootstrap: 是否随机有放回, n_jobs: 可并行运行的数量
    rf = RandomForestClassifier(n_estimators=25, criterion='entropy', bootstrap=True, n_jobs=4, random_state=80)  # 随机森林
    return fit(rf, 'rf')


def adaboost():
    ada = AdaBoostClassifier(
        tree.DecisionTreeClassifier(criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1), \
        algorithm="SAMME", n_estimators=200, learning_rate=0.8)
    return fit(ada, 'ada')


def fit(clf, s):
    t3 = datetime.datetime.now()
    X_train = joblib.load(train_list.split('.')[0] + filename)
    y_train = joblib.load(train_list.split('.')[0] + '_label.pkl')
    clf = clf.fit(X_train, y_train)
    joblib.dump(clf, s + '_model.pkl')
    t4 = datetime.datetime.now()
    print("--------------------------------\ntime of training model: %0.2f" % (t4 - t3).total_seconds())
    scores = cross_val_score(clf, X_train, y_train, scoring='accuracy')
    print("Train Cross Avg. Score: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    return clf


def testScore(clf):
    t4 = datetime.datetime.now()
    X_test = joblib.load(test_list.split('.')[0] + filename)
    y_test = joblib.load(test_list.split('.')[0] + '_label.pkl')
    print("x-test:")
    print(X_test)
    print("y-test:")
    print(y_test)
    clf_score = clf.score(X_test, y_test)
    print("--------------------------------\nTest score: %.4f" % clf_score)
    clf_pred = clf.predict(X_test)
    print(clf_pred[:3])
    t5 = datetime.datetime.now()
    print("time of testing model: %0.2f" % (t5 - t4).total_seconds())
    scores = cross_val_score(clf, X_test, y_test, scoring='accuracy')
    print(scores.max(), scores.min(), type(scores))
    print("Test Cross Avg. Score: %0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2))
    if clf_pred[:1] == 0:
        if scores[:1] > 0.5: #negative
            return False
        else:
            return True
    elif clf_pred[:1] == 1:
        if scores[:1] > 0.5: #positive
            return True
        else:
            return False

# if __name__ == '__main__':
#    save_feature()
#
#    # dt = decision_tree()
#    # rf = random_forest()
#    ada = adaboost()
#    # dt = joblib.load('dt_model.pkl')
#    # rf = joblib.load('rf_model.pkl')
#    ada = joblib.load('ada_model.pkl')
#    print(testScore(ada))
