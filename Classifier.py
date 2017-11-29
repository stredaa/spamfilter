# coding=UTF-8
import numpy
import math
from abc import ABCMeta, abstractmethod
from cvxpy import *


class Classifier(object):
    """Abstract class from which all classifiers should be derived.
    Provides basic interfacing in order to train/evaluate."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def evaluate(self, sample):
        """Evaluate given sample according to the trained constants.
        Sign of returned value corresponds to the result.

        :param sample: A vectorized sample (list).
        """
        pass

    @abstractmethod
    def __init__(self, data, labels):
        """Initialize model - derive model parameters from given
        data and its labels.

        :param data: A list of vectorized samples.
        :param labels: A 1/0 vector symbolizing positive/negative
        detection.
        """
        pass


class LogisticClassifier(Classifier):
    """A classifier based on a logistic curve."""
    __a = None
    __b = None

    @staticmethod
    def getModelParams(data, labels, size):
        """Calculate logistic-regression classifier parameters.s

        :param data: A list of vectorized samples.
        :param labels: A 1/0 vector symbolizing positive/negative
        detection.
        :param size: The length of given dataset.
        """
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
        """Evaluate given sample according to calculated model.
        Return a value in (-1/2, 1/2) with sign corresponding
        to positive/negative detection.

        :param sample: A vectorized sample.
        """
        if self.__a is None or self.__b is None:
            raise ValueError("Model parameters not set!")
        return (math.e**(sample * self.__a + self.__b)[0, 0] /
                (1 + math.e**(sample * self.__a + self.__b)[0, 0]) - 1.0 / 2)

    def __init__(self, data, labels):
        """Initialize logistic curve parameters from a given labeled
        dataset._

        :param data: A list of vectorized samples.
        :param labels: A 1/0 vector symbolizing pozitive/negative
        detection.
        """
        self.__a, self.__b = LogisticClassifier.getModelParams(
            numpy.matrix(data), labels, len(data[0]))


class SVMClassifier(Classifier):
    """Classifier class based on support vector machines."""
    alpha = None
    tau = None
    x = None

    @staticmethod
    def gaussKernel(a, tau):
        """Return Gaussian kernel matrix.

        :param a: list of mails
        :param tau: kernel coefficient number
        """
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
        """ Finds and stores optimal model parameters.
        :param x: A list of vectorized samples.
        :param y: A 1/0 vector symbolizing positive/negative detection
        :param tau: kernel coefficient
        :param C: penalty coefficient
        :param limit: relevance limit for alpha
        """
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
        """Evaluate a given sample according to given mode. A sign
        of returned value corresponds to positive/negative detection.

        :param sample: A vectorized sample.
        """
        if self.alpha is None or self.x is None or self.tau is None:
            raise ValueError("Model parameters not set!")
        sample = 1 * (numpy.array(sample) > 0)
        tmp = self.x - sample
        return numpy.sum(numpy.multiply(numpy.exp(
            - numpy.linalg.norm(tmp, axis=1)**2 / (2 * self.tau**2)),
            self.alpha))

    def __init__(self, data, labels, tau=8, C=3, limit=1e-3):
        """Initialize logistic curve parameters from a given labeled
        dataset._

        :param data: A list of vectorized samples.
        :param labels: A 1/0 vector symbolizing pozitive/negative
        detection.
        """

        self.tau = tau
        self.alpha, self.x = SVMClassifier.getModelParams(
            numpy.array(data), numpy.array(labels), tau, C, limit)
