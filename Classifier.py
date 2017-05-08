import numpy
import math
from cvxpy import *

class Classifier(object):
    #Classify sample
    def evaluate(self, sample):
        None

    #Initialize inner parameters
    def __init__(self, data, labels):
        None

class LogisticClassifier(Classifier):
    a = None
    b = None

    #CVXPY convex optimization solver, given vectorized emailes it tries to find optimal parameter values for logistic regression curve.
    @staticmethod
    def getModelParams(data, labels, size):
        a = Variable(size, 1)
        b = Variable()
        spam = sum(labels)
        testing = numpy.matrix(labels)

        logLogistic = sum([logistic(data[i] * a + b) for i in xrange(len(data))])
        positive = testing * data * a  + b * spam
        problem = Problem(Maximize(positive - logLogistic))

        result = problem.solve(solver=SCS)
        return a.value, b.value

    #Classify sample
    def evaluate(self, sample):
        if self.a is None or self.b is None:
            raise ValueError("Model parameters not set!")
        return math.e**(sample * self.a + self.b)[0, 0] / (1 + math.e**(sample * self.a + self.b)[0, 0])

    def __init__(self, data, labels):
        self.a, self.b = Classifier.getModelParams(numpy.matrix(data), labels, len(data[0]))
