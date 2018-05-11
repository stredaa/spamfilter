import spamfilter
import DictionaryUtils
import Parser
import Classifier
import pickle


def get_msgs(files, limit):
    mails = [spamfilter.mbox_extract(x)[:limit] for x in files]

    total = 0
    corpus = []

    for l in mails:
        if len(l) < limit / len(mails):
            total += len(l)
            for mail in l:
                corpus.append(mail)

    for l in mails:
        if len(l) >= limit / len(mails):
            for mail in l[:(limit - total) // len(mails)]:
                corpus.append(mail)
    return corpus


def train(ham_files, spam_files, limit=1000, dict_limit=250,
          persistence_location="/tmp/", name="test_acc"):
    """Create a model from given sets of files.

    Args:
        ham_files (list): list of file paths to HAM mboxes
        spam_files (list): list of file paths to SPAM mboxes
        persistence_location (str): directory where model should be stored
        name (str): model name prefix
    """
    def build_base_dict(mail, dictionary, frequency):
        raw = Parser.ParserDictionary.stripHeaders(mail).lower()
        return DictionaryUtils.Dictionary.createDictionary([raw],
                                                           dictionary,
                                                           frequency)

    ham = get_msgs(ham_files, limit)
    spam = get_msgs(spam_files, limit)

    dHam, fHam, dSpam, fSpam = [], [], [], []
    for mail in ham:
        dHam, fHam = build_base_dict(mail, dHam, fHam)
    for mail in spam:
        dSpam, fSpam = build_base_dict(mail, dSpam, fSpam)

    optimized_dictionary = DictionaryUtils.DictionaryMI.filterDictionary(
        dSpam, fSpam, dHam, fHam
    )

    parser = Parser.ParserDictionary(optimized_dictionary)
    classifier = Classifier.LogisticClassifier(
        [parser.parseEmail(x) for x in spam + ham],
        [1] * len(spam) + [0] * len(ham)
    )

    pickle.dump({"classifier": classifier, "parser": parser},
                open(persistence_location + name + "_model.p", "wb"))


def evaluate(email_path, persistence_location="/tmp/", name="test_acc"):
    """Evaluate e-mails spaminess.
    Args:
        email_path (str): path to e-mail to be tested
    Returns:
        float: (-1,1) where value over 0 corresponds to positive SPAM
        evaluation
    """
    data = pickle.load(open(persistence_location + name + "_model.p", "rb"))
    classifier, parser = data["classifier"], data["parser"]

    mail = spamfilter.mbox_extract(email_path)[0]
    return classifier.evaluate(parser.parseEmail(mail)) * 2
