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
    def gaussKernel(a, b, tau):
        Ker = numpy.zeros((len(a), len(b)))
        for i in range(len(a)):
            for j in range(len(b)):
                Ker[i, j] = numpy.exp(
                    -(numpy.linalg.norm(a[i] -
                                        b[j], 2))**2 / (2 * tau * tau))
        return Ker

    @staticmethod
    def getModelParams(x, y, tau, C):
        m = len(y)
        x = 1 * (x > 0)
        y = 2 * y - 1
        Ker = SVMClassifier.gaussKernel(x, x, tau)
        alpha = Variable(m)
        loss = sum_entries(pos(1 - mul_elemwise(y,  Ker * alpha))
                           ) + quad_form(alpha, Ker) / (2 * C)
        problem = Problem(Minimize(loss))
        problem.solve()
        return alpha.value, x

    def evaluate(self, sample):
        if self.alpha is None or self.x is None or self.tau is None:
            raise ValueError("Model parameters not set!")
        sample = numpy.transpose(numpy.array(sample))
        sample = 1 * (sample > 0)
        res = 0
        for i in xrange(len(self.alpha)):
            res = res + self.alpha[i] * numpy.exp(-(numpy.linalg.norm(
                self.x[i] - sample, 2))**2 / (2 * self.tau * self.tau))
        return res

    def __init__(self, data, labels, tau=8, C=3):
        self.tau = tau
        self.alpha, self.x = SVMClassifier.getModelParams(
            numpy.array(data), numpy.array(labels), tau, C)
