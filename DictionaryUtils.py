class DictionaryUtils(object):
    #Create a dictionary with frequencies from a set of emails.
    @staticmethod
    def createDictionary(files, dictionary = [], frequency = []):
        tmpDict = []
        tmpFreq = []
        tmpAppends = []

        #Create small dict
        for file in files:
            for word in file.split(" "):
                if word in tmpDict:
                    tmpFreq[tmpDict.index(word)] += 1
                else:
                    tmpDict.append(word)
                    tmpFreq.append(1)

        #Merge old and new dict
        for i in xrange(len(tmpDict)):
            if tmpDict[i] in dictionary:
                frequency[dictionary.index(tmpDict[i])] += tmpFreq[i]
            else:
                tmpAppends.append(tmpDict[i])
                frequency.append(tmpFreq[i])

        return dictionary + tmpAppends, frequency

    #Filter dictionary entries.
    @staticmethod
    def filterDictionary(dHam, fHam, dSpam, fSpam): #Array of emails
        return None
