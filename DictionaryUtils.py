from abc import ABCMeta, abstractmethod
import math


class Dictionary(object):
    __metaclass__ = ABCMeta

    @staticmethod
    def createDictionary(files, dictionary, frequency):
        """Create a dictionary with frequencies from a set of emails."""
        tmpDict = []
        tmpFreq = []
        tmpAppends = []

#        Create small dict
        for file in files:
            for word in file.split(" "):
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
    def filterDictionary(dHam, fHam, dSpam, fSpam):
        """Filter dictionary entries"""
        pass


class DictionaryMI(Dictionary):
    @staticmethod
    def mutualInformation(dSpam, fSpam, dHam, fHam):
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
            MI = mutualInformationSummand(fSpam[i], fOpp, len(dSpam), len(dHam))
            MI += mutualInformationSummand(fOpp, fSpam[i], len(dHam), len(dSpam))
            mSpam += [{"word": dSpam[i], "MI": MI}]
        for i in xrange(len(dHam)):
            if dHam[i] not in dSpam:
                MI = mutualInformationSummand(fHam[i], 0, len(dHam), len(dSpam))
                mSpam += [{"word": dHam[i], "MI": MI}]
        return mSpam

    @staticmethod
    def filterDictionary(dSpam, fSpam, dHam, fHam):
        MI = DictionaryMI.mutualInformation(dSpam, fSpam, dHam, fHam)
        sMI = sorted(MI, key=lambda k: -k['MI'])
        return [i['word'] for i in sMI]
