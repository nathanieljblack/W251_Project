#Configuration

Ubuntu 14.04  
64GB RAM  
16 CPU  
200GB Disk  
  
#Model

Attempted to fit Naive Bayes model on the 36GB training data set using ``nb_sklearn.py``. The process ran for 2 hours but consistently ran out of memory when trying to fit the data. Such errors on a high performance machine lead us to believe that a distributed solution is appropriate for our problem.

#Log  

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
