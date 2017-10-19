import os
import pickle
import resource
import argparse
import mailbox
import time
import hashlib

from Parser import *
from Classifier import *
from DictionaryUtils import *


def setRamLimit(limit):
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))


def extractMBOX(filename):
    def getBody(msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get('Content-Disposition') is not None and \
                   ("attachment" in
                        part.get('Content-Disposition') or
                    "inline" in
                        part.get('Content-Disposition')):
                    continue
                if part.is_multipart():
                    for subpart in part.walk():
                        try:
                            if ("attachment" in
                                    subpart.get('Content-Disposition') or
                                "inline" in
                                    subpart.get('Content-Disposition')):
                                continue
                            body += subpart.get_payload(decode=True)
                        except:
                            pass
                else:
                    try:
                        body += part.get_payload(decode=True)
                    except:
                        pass
        else:
            try:
                body += msg.get_payload(decode=True)
            except:
                pass
        return body
    mbox = mailbox.mbox(filename)
    return list(map(getBody, mbox))


def retrieveFile(filename, limit):
    if not os.path.exists(filename):
        print "[error]\tFile " + filename + " does not exist."
        raise Exception("File " + filename + " not existing.")
    if filename[-2:] == ".p":
        print "[info]\tFile " + filename + " opened as pickled file."
        return pickle.load(open(filename, "rb"))[:limit]
    elif filename[-5:] == ".mbox":
        print "[info]\tFile " + filename + " opened as mbox."
        return extractMBOX(filename)[:limit]
    else:
        print "[info]\tFile " + filename + " as a raw text file."
        with open(filename, "rb") as f:
            return [f.read()]


def buildModel(ham, spam, dictLimit):
    def buildBaseDict(mail, dictionary, frequency):
        raw = ParserDictionary.stripHeaders(mail).lower()
        return Dictionary.createDictionary([raw], dictionary, frequency)

    start = int(time.time())

    dHam, fHam, dSpam, fSpam = [], [], [], []
    for mail in ham:
        dHam, fHam = buildBaseDict(mail, dHam, fHam)
    print "[info]\tHAM processed"
    for mail in spam:
        dSpam, fSpam = buildBaseDict(mail, dSpam, fSpam)
    print "[info]\tSPAM processed"
    if "mi-" in args.algo:
        optimizedDictionary = DictionaryMI.filterDictionary(
            dSpam, fSpam, dHam, fHam
        )[:dictLimit]
        print "[info]\tCreated MI-optimized dictionary"
    parser = ParserDictionary(optimizedDictionary)
    if "-svm" in args.algo:
        classifier = SVMClassifier(
            map(lambda x: parser.parseEmail(x), spam + ham),
            [1] * len(spam) + [0] * len(ham)
        )
        print "[info]\tCreated SVM classifier."
    elif "-logistic" in args.algo:
        classifier = LogisticClassifier(
            map(lambda x: parser.parseEmail(x), spam + ham),
            [1] * len(spam) + [0] * len(ham)
        )
        print "[info]\tCreated Logistic-regression classifier"
    print "[stat]\tTime taken: " + str(int(time.time())-start)
    return classifier, parser


def runTests(emails, classifier, parser):
    def makeStatistics(data):
        results = map(lambda x: int(x > 0), data.values())
        print "[stat]\tTotal items: " + str(len(results))
        print "[stat]\tTotal items classified as spam: " + str(sum(results))
        print ("[stat]\t" + "Percentage of items classified as spam: "
               '{0:.2f}'.format(100.0 * sum(results) / len(results)) + "%")

    def evalMsg(result, msg, classifier, parser):
        sha256 = hashlib.sha256()
        sha256.update(msg)
        result[sha256.hexdigest()] = \
                classifier.evaluate(parser.parseEmail(msg))

    result = {}
    map(lambda x: evalMsg(result, x, classifier, parser), emails)
    makeStatistics(result)
    return result

parser = argparse.ArgumentParser(
    description='Create a spamfilter model or apply a created filter.')
parser.add_argument('--ham',
                    help="A file containing HAM.")
parser.add_argument('--spam',
                    help="A file containing SPAM")
parser.add_argument('--mail',
                    help="A file containing unsorted mail")
parser.add_argument('-o', '--output', help="output file", default="model.p")
parser.add_argument('-m', '--model', help="model file", default="model.p")
parser.add_argument("mode", help="Set program mode",
                    choices=["model", "test"])
parser.add_argument('-a', "--algo", help="Select training algorithms.",
                    choices=["mi-logistic",
                             "mi-svm"], default="mi-logistic")
parser.add_argument("-l", "--limit", default=500,
                    help="Import set limit - memory limitation", type=int)
parser.add_argument("-d", "--dictLimit", default=250,
                    help="Max dictionary size", type=int)
parser.add_argument("-r", "--ramLimit", type=int,
                    help="Set RAM limit (MB) -- OOM prevent.")

args = parser.parse_args()

if args.ramLimit:
    setRamLimit(args.ramLimit * 10**6)

if args.mode == "model":
    if not args.ham or not args.spam:
        print "--ham and --spam parameters are required"
    ham = retrieveFile(args.ham, args.limit)
    spam = retrieveFile(args.spam, args.limit)

    classifier, parser = buildModel(ham, spam, args.dictLimit)
    pickle.dump({"classifier": classifier, "parser": parser},
                open(args.output, "wb"))

elif args.mode == "test":
    def unpickleModel(filename):
        data = pickle.load(open(filename, "rb"))
        return data["classifier"], data["parser"]

    emails = retrieveFile(args.mail, args.limit)
    classifier, parser = unpickleModel(args.model)
    results = runTests(emails, classifier, parser)

    if not args.mail:
        print "--mail parameter is required"
#    print results

else:
    raise Exception("You have to set a valid model.")
