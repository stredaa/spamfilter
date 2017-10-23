import numpy
import math
from abc import ABCMeta, abstractmethod
from cvxpy import *


class Classifier(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate(self, sample):
        None

    @abstractmethod
    def __init__(self, data, labels):
        None


class LogisticClassifier(Classifier):
    a = None
    b = None

    @staticmethod
    def getModelParams(data, labels, size):
        a = Variable(size, 1)
        b = Variable()
        spam = sum(labels)
        testing = numpy.matrix(labels)

        logLogistic = sum([logistic(data[i] * a + b)
                           for i in xrange(len(data))])
        positive = testing * data * a + b * spam
        problem = Problem(Maximize(positive - logLogistic))

        problem.solve(solver=SCS)
        return a.value, b.value

    def evaluate(self, sample):
        if self.a is None or self.b is None:
            raise ValueError("Model parameters not set!")
        return (math.e**(sample * self.a + self.b)[0, 0] /
                (1 + math.e**(sample * self.a + self.b)[0, 0]) - 1.0 / 2)

    def __init__(self, data, labels):
        self.a, self.b = LogisticClassifier.getModelParams(
            numpy.matrix(data), labels, len(data[0]))


class SVMClassifier(Classifier):
    alpha = None
    tau = None
    x = None

    @staticmethod
    def gaussKernel(a, tau):
        dim = len(a)
        Ker = numpy.zeros((dim, dim))
        for i in range(dim):
            for j in range(i, dim):
                Ker[i, j] = -(numpy.linalg.norm(a[i] - a[j], 2))**2
                Ker[j, i] = Ker[i, j]
        Ker = numpy.exp(Ker / (2 * tau**2))
        return Ker

    @staticmethod
    def getModelParams(x, y, tau, C, limit):
        m = len(y)
        x = 1 * (x > 0)
        y = 2 * y - 1
        Ker = SVMClassifier.gaussKernel(x, tau)
        alpha = Variable(m)
        loss = sum_entries(pos(1 - mul_elemwise(y,  Ker * alpha))
                           ) + quad_form(alpha, Ker) / (2 * C)
        problem = Problem(Minimize(loss))
        problem.solve(solver=ECOS, verbose=False, max_iters=15)
        # Only alphas with absolute value > limit are relevant
        a = numpy.array(alpha.value.T)[0]
        newX = []
        newA = []
        for i in xrange(len(a)):
            if numpy.abs(a[i]) > limit:
                newA.append(a[i])
                newX.append(x[i])

        return numpy.array(newA), numpy.array(newX)

    def evaluate(self, sample):
        if self.alpha is None or self.x is None or self.tau is None:
            raise ValueError("Model parameters not set!")
        sample = 1 * (numpy.array(sample) > 0)
        tmp = self.x - sample
        return numpy.sum(numpy.multiply(numpy.exp(-numpy.linalg.norm(tmp, axis=1)**2 / (2 * self.tau**2)), self.alpha))

    def __init__(self, data, labels, tau=8, C=3, limit=1e-3):
        self.tau = tau
        self.alpha, self.x = SVMClassifier.getModelParams(
            numpy.array(data), numpy.array(labels), tau, C, limit)
