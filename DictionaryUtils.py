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

        tmpDict = []
        tmpFreq = []
        tmpAppends = []

#        Create small dict
        for file in files:
            for word in filter(lambda x: len(x) < 50, file.split(" ")):
                if word in tmpDict:
                    tmpFreq[tmpDict.index(word)] += 1
                else:
                    tmpDict.append(word)
                    tmpFreq.append(1)

#       Merge old and new dict
        for i in xrange(len(tmpDict)):
            if tmpDict[i] in dictionary:
                frequency[dictionary.index(tmpDict[i])] += tmpFreq[i]
            else:
                tmpAppends.append(tmpDict[i])
                frequency.append(tmpFreq[i])

        return dictionary + tmpAppends, frequency

    @staticmethod
    @abstractmethod
    def filterDictionary(dSpam, fSpam, dHam, fHam):
        """Abstract method intended for dictionary filtering.

        :param dSpam: list of strings (words) - dictionary of SPAM dataset
        :param fSpam: list of integers - associated HAM frequencies
        :param dHam: list of strings (words) - dictionary of HAM dataset
        :param fHam: list of integers - associated HAM frequencies
       """
        pass


class DictionaryMI(Dictionary):
    """Dictionary extraction class with filtering based on a
    mutual information."""
    @staticmethod
    def mutualInformation(dSpam, fSpam, dHam, fHam):
        """Generate a dictionary keyed by strings (words) with a corresponding
        I_mutual as a value.

        :param dSpam: list of strings (words) - dictionary of SPAM dataset
        :param fSpam: list of integers - associated HAM frequencies
        :param dHam: list of strings (words) - dictionary of HAM dataset
        :param fHam: list of integers - associated HAM frequencies
        """
        def mutualInformationSummand(fSel, fOpp, tSel, tOpp):
            p_xy = 1.0 * fSel / (tSel + tOpp)
            p_x = (fSel + fOpp) * 1.0 / (tSel + tOpp)
            p_y = tSel * 1.0 / (tSel + tOpp)
            if p_xy / (p_x * p_y) > 0:
                return p_xy * math.log(p_xy / (p_x * p_y))
            else:
                return 0

        mSpam = []
        for i in xrange(len(dSpam)):
            if dSpam[i] in dHam:
                fOpp = fHam[dHam.index(dSpam[i])]
            else:
                fOpp = 0
            MI = mutualInformationSummand(
                fSpam[i], fOpp, len(dSpam), len(dHam))
            MI += mutualInformationSummand(
                fOpp, fSpam[i], len(dHam), len(dSpam))
            mSpam += [{"word": dSpam[i], "MI": MI}]
        for i in xrange(len(dHam)):
            if dHam[i] not in dSpam:
                MI = mutualInformationSummand(
                    fHam[i], 0, len(dHam), len(dSpam))
                mSpam += [{"word": dHam[i], "MI": MI}]
        return mSpam

    @staticmethod
    def filterDictionary(dSpam, fSpam, dHam, fHam):
        """Create a dictionary keyed by strings (words) with a corresponding
        mutual information value. Use these values to sort the keys.

        :param dSpam: list of strings (words) - dictionary of SPAM dataset
        :param fSpam: list of integers - associated HAM frequencies
        :param dHam: list of strings (words) - dictionary of HAM dataset
        :param fHam: list of integers - associated HAM frequencies
        """
        MI = DictionaryMI.mutualInformation(dSpam, fSpam, dHam, fHam)
        sMI = sorted(MI, key=lambda k: -k['MI'])
        return [i['word'] for i in sMI]
