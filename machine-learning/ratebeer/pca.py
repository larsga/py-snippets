
import rblib
from numpy import *

def pca(data, n = 999999):
    themean = mean(data, axis = 0)
    mean_removed = data - themean
    covariance = cov(mean_removed, rowvar = 0)
    (eigvals, eigvecs) = linalg.eig(mat(covariance))

    eigval_indices = argsort(eigvals)[ : -(n + 1) : -1]
    eigvecs = eigvecs[ : , eigval_indices]

    low_density = mean_removed * eigvecs
    recon_mat = (low_density * eigvecs.T) + themean
    return (low_density, recon_mat)

def eigenvalues(data, columns):
    covariance = cov(data - mean(data, axis = 0), rowvar = 0)
    eigvals = linalg.eig(mat(covariance))[0]
    indices = list(argsort(eigvals))
    indices.reverse() # so we get most significant first
    return [(columns[ix], float(eigvals[ix])) for ix in indices]

(scores, parameters, columns) = rblib.load_as_matrix('ratings.txt')
for (col, ev) in eigenvalues(parameters, columns):
    print "%40s   %s" % (col, float(ev))
