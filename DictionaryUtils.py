from abc import ABCMeta, abstractmethod
import math


class Dictionary(object):
    """Abstract dictionary class, already can extract dictionary
    from a string but it is necessary to implement dictionary filtering"""
    __metaclass__ = ABCMeta

    @staticmethod
    def createDictionary(files, dictionary, frequency):
        """Return a dictionary and associated frequencies from a given corpus.

        :param files: array of strings containing the corpus
        :param dictionary: list of strings (words) to be extended
        :param frequency: list of integers (frequencies) to be extended
        """

        tmp_dict = []
        tmp_freq = []
        tmp_appends = []

#        Create small dict
        for file in files:
            for word in filter(lambda x: 0 < len(x) < 50, file.split(" ")):
                if word in tmp_dict:
                    tmp_freq[tmp_dict.index(word)] += 1
                else:
                    tmp_dict.append(word)
                    tmp_freq.append(1)

#       Merge old and new dict
        for i in xrange(len(tmp_dict)):
            if tmp_dict[i] in dictionary:
                frequency[dictionary.index(tmp_dict[i])] += tmp_freq[i]
            else:
                tmp_appends.append(tmp_dict[i])
                frequency.append(tmp_freq[i])

        return dictionary + tmp_appends, frequency

    @staticmethod
    @abstractmethod
    def filterDictionary(spam_d, spam_f, ham_d, ham_f):
        """Abstract method intended for dictionary filtering.

        :param spam_d: list of strings (words) - dictionary of SPAM dataset
        :param spam_f: list of integers - associated HAM frequencies
        :param ham_d: list of strings (words) - dictionary of HAM dataset
        :param ham_f: list of integers - associated HAM frequencies
       """
        pass


class DictionaryMI(Dictionary):
    """Dictionary extraction class with filtering based on a
    mutual information."""
    @staticmethod
    def mutualInformation(spam_d, spam_f, ham_d, ham_f):
        """Generate a dictionary keyed by strings (words) with a corresponding
        I_mutual as a value.

        :param spam_d: list of strings (words) - dictionary of SPAM dataset
        :param spam_f: list of integers - associated HAM frequencies
        :param ham_d: list of strings (words) - dictionary of HAM dataset
        :param ham_f: list of integers - associated HAM frequencies
        """
        def mutualInformationSummand(sel_freq, opp_freq, sel_total, opp_total):
            p_xy = 1.0 * sel_freq / (sel_total + opp_total)
            p_x = (sel_freq + opp_freq) * 1.0 / (sel_total + opp_total)
            p_y = sel_total * 1.0 / (sel_total + opp_total)
            if p_xy / (p_x * p_y) > 0:
                return p_xy * math.log(p_xy / (p_x * p_y))
            else:
                return 0

        spam_m = []
        for i in xrange(len(spam_d)):
            if spam_d[i] in ham_d:
                opp_freq = ham_f[ham_d.index(spam_d[i])]
            else:
                opp_freq = 0
            MI = mutualInformationSummand(
                spam_f[i], opp_freq, len(spam_d), len(ham_d))
            MI += mutualInformationSummand(
                opp_freq, spam_f[i], len(ham_d), len(spam_d))
            spam_m += [{"word": spam_d[i], "MI": MI}]
        for i in xrange(len(ham_d)):
            if ham_d[i] not in spam_d:
                MI = mutualInformationSummand(
                    ham_f[i], 0, len(ham_d), len(spam_d))
                spam_m += [{"word": ham_d[i], "MI": MI}]
        return spam_m

    @staticmethod
    def filterDictionary(spam_d, spam_f, ham_d, ham_f):
        """Create a dictionary keyed by strings (words) with a corresponding
        mutual information value. Use these values to sort the keys.

        :param spam_d: list of strings (words) - dictionary of SPAM dataset
        :param spam_f: list of integers - associated HAM frequencies
        :param ham_d: list of strings (words) - dictionary of HAM dataset
        :param ham_f: list of integers - associated HAM frequencies
        """
        MI = DictionaryMI.mutualInformation(spam_d, spam_f, ham_d, ham_f)
        sMI = sorted(MI, key=lambda k: -k['MI'])
        return [i['word'] for i in sMI]
