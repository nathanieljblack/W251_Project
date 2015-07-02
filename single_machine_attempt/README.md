#Configuration

Ubuntu 14.04  
64GB RAM  
16 CPU  
200GB Disk  
  
#Model

Attempted to fit Naive Bayes model on the 36GB training data set using ``nb_sklearn.py``. The process ran for 2 hours but consistently ran out of memory when trying to fit the data. Such errors on a high performance machine lead us to believe that a distributed solution is appropriate for our problem.

#256x256
```
root@master:~# time python nb_sklearn.py
Traceback (most recent call last):
  File "nb_sklearn.py", line 77, in <module>
    main()
  File "nb_sklearn.py", line 56, in main
    nb.fit(x,y)
  File "/root/anaconda/lib/python2.7/site-packages/sklearn/naive_bayes.py", line 324, in fit
    self._count(X, Y)
  File "/root/anaconda/lib/python2.7/site-packages/sklearn/naive_bayes.py", line 427, in _count
    self.feature_count_ += safe_sparse_dot(Y.T, X)
  File "/root/anaconda/lib/python2.7/site-packages/sklearn/utils/extmath.py", line 180, in safe_sparse_dot
    return fast_dot(a, b)
MemoryError

real    143m43.574s
user    142m51.321s
sys     0m46.550s
```

#16x16 

Drastically reducing the size of the images allows for the computation to be run but it also removes most of the pertinent information (i.e. the prediction is bad).

```
root@master:~# time python nb_sklearn.py
precision    recall  f1-score   support

0       0.85      0.01      0.01     25810
1       0.09      0.21      0.12      2443
2       0.19      0.01      0.01      5292
3       0.03      0.49      0.05       873
4       0.02      0.45      0.05       708

avg / total       0.66      0.04      0.02     35126


real    142m23.711s
user    142m4.134s
sys     0m17.781s
root@master:~# 
```

#32x32

```
root@master:~# top -b | python nb_sklearn.py
             precision    recall  f1-score   support

          0       0.80      0.00      0.01     25810
          1       0.09      0.21      0.12      2443
          2       0.18      0.01      0.02      5292
          3       0.03      0.49      0.05       873
          4       0.02      0.44      0.05       708

avg / total       0.62      0.04      0.02     35126

root@master:~# 
```

#64x64

```
0.0409383362751


             precision    recall  f1-score   support

          0       0.84      0.00      0.01     25810
          1       0.09      0.22      0.12      2443
          2       0.17      0.01      0.02      5292
          3       0.03      0.49      0.05       873
          4       0.02      0.44      0.05       708

avg / total       0.65      0.04      0.02     35126


real    142m50.699s
user    142m19.824s
sys     0m29.175s
```

#128x128

```
root@master:~# time python nb_sklearn.py
0.0411091499174


             precision    recall  f1-score   support

          0       0.83      0.00      0.01     25810
          1       0.09      0.22      0.12      2443
          2       0.16      0.01      0.02      5292
          3       0.03      0.49      0.05       873
          4       0.02      0.44      0.05       708

avg / total       0.64      0.04      0.02     35126


real    144m19.923s
user    143m13.548s
sys     1m4.569s
```


#16x16
Logistic Regression

```
root@master:~# time python lr_sklearn.py
0.774753743666


             precision    recall  f1-score   support

          0       0.78      0.98      0.87     25810
          1       0.72      0.09      0.16      2443
          2       0.61      0.16      0.25      5292
          3       0.87      0.32      0.47       873
          4       0.99      0.80      0.89       708

avg / total       0.75      0.77      0.72     35126


real    681m33.367s
user    667m29.785s
sys     0m32.937s
```