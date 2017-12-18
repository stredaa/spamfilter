import unittest
from DictionaryUtils import *
from Parser import *


# DicUtils
class TestDictUtils(unittest.TestCase):

    def test_createDictionary(self):
        files = [' a  b c ', 'a b d']
        dic = ['a', 'e']
        freq = [5, 6]
        dicRes = ['a', 'e', 'b', 'c', 'd']
        freqRes = [5 + 2, 6, 2, 1, 1]
        self.assertEqual(Dictionary.createDictionary(
            files, dic, freq), (dicRes, freqRes))

        files = ['a c', 'a b']
        dic = []
        freq = []
        dicRes = ['a', 'c', 'b']
        freqRes = [2, 1, 1]
        self.assertEqual(Dictionary.createDictionary(
            files, dic, freq), (dicRes, freqRes))

        files = ['']
        dic = ['a', 'e']
        freq = [5, 6]
        dicRes = ['a', 'e']
        freqRes = [5, 6]
        self.assertEqual(Dictionary.createDictionary(
            files, dic, freq), (dicRes, freqRes))


# Parser
class TestParser(unittest.TestCase):

    def test_parseEmail(self):

        # Tests for ParserDictionary
        parser = ParserDictionary(['a', 'b', 'c'])
        self.assertEqual(parser.parseEmail('A c d a'), [2, 0, 1])
        parser = ParserDictionary(['a', 'b', 'c'])
        self.assertEqual(parser.parseEmail(' '), [0, 0, 0])


if __name__ == '__main__':
    unittest.main()
