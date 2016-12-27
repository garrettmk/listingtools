from unittest import TestCase
from quantityguesser import QuantityGuesser
from itertools import chain


class TestQuantityGuesser(TestCase):

    mult_set = ((['12', '12'], 144),
                (['1,000', '2'], 2000),
                (['1,000', '1/2'], 500),
                (['each', 'doz'], 12),
                (['pair', 'pr'], 4),
                (['pc', 'doz'], 12),
                (['2', 'dozen'], 24),
                (['1/2', '  dz'], 6),
                (['2 ', 'PAIR'], 4),
                (['lkjlf', 'lkdjf'], 1),
                (['dozen'], 12),
                ([], 1))

    type1_set = (('Pack of 12', 12),
                 ('packs of (12)', 12),
                 ('pk of 1dz', 12),
                 ('cases of 1 dozen', 12),
                 ('cs of 1,000', 1000),
                 ('case of 1/2 dz', 6),
                 ('set of (1/2) doz', 6),

                 ('sets consist of 12', 12),
                 ('box consists of (12)', 12),
                 ('boxes consist of 1 dozen', 12),
                 ('bags consist of (1) dz', 12),
                 ('case consists of 1,000 pieces', 1000),
                 ('set consists of (1,000/2) pcs', 500),

                 ('30 sets of 100', 3000),
                 ('10 packs of 1 dz', 120),
                 ('(10) boxes of 1/2 dozen', 60),
                 ('1 set of (10) pieces', 10),
                 ('2 sets of 1/2dz', 12),
                 ('(12) boxes of 1,000 units', 12000))

    type2_set = (('12pk', 12),
                 ('12 pack', 12),
                 ('12-pack', 12),
                 ('12/pack', 12),
                 ('12 / set', 12),
                 ('12 per carton', 12),
                 ('1/2 doz per set', 6),

                 ('(12)pk', 12),
                 ('(12) pack', 12),
                 ('(12)-pack', 12),
                 ('(12)/set', 12),
                 ('(12) per carton', 12),
                 ('(1,000/2)/box', 500),

                 ('1dz pack', 12),
                 ('1 dozen - pack', 12),
                 ('1dz / set', 12),
                 ('1 dozen per box', 12),
                 ('1 doz per set', 12),

                 ('1,000 pk', 1000),
                 ('1,000-pack', 1000),
                 ('1,000/set', 1000),
                 ('1,000 per case', 1000),

                 ('12 pieces / set', 12),
                 ('12 bloops/set', 12),
                 ('12ears/set', 12),
                 ('1dz bloops / set', 12),
                 ('12pc per case', 12),
                 ('(12) pieces / box', 12),
                 ('(12) bloops per carton', 12),
                 ('(1,000) pieces / case', 1000),
                 ('1dz bloops per box', 12),
                 ('(1) dz pieces/set', 12),
                 ('1/2 doz / set', 6))

    type3_set = (('1dz', 12),
                 ('1-dozen', 12),
                 ('(6) each', 6),
                 ('2 pair', 4),
                 ('12-piece', 12),
                 ('12 piece', 12),
                 ('(12)/piece', 12),
                 ('1,000 pcs', 1000),
                 ('case (12) dozen', 144))

    nonsense_set = (('doesn\'t look like anything to me', None),
                    ('12345 castor wheels', None),
                    ('12345 stand', None),
                    ('15/2016 by Steve', None),
                    ('st990', None),
                    ('1 fact', None),
                    ('blasts of 10 meters', None))

    def setUp(self):
        self.guesser = QuantityGuesser()

    def test__mult_(self):
        """Test the _mult() method."""
        for test_params in self.mult_set:
            with self.subTest(string=' * '.join(test_params[0])):
                self.assertEqual(self.guesser._mult(*test_params[0]), test_params[1])

        for params in self.nonsense_set:
            with self.subTest(string=params[0]):
                self.assertEqual(self.guesser._mult(params[0]), 1)

    def test__type1_matches(self):
        """Test _type1_matches()."""
        for params in self.type1_set:
            with self.subTest(string=params[0]):
                self.assertEqual(next(self.guesser._type1_matches(params[0])), params[1])

        for params in self.nonsense_set:
            with self.subTest(string=params[0]):
                with self.assertRaises(StopIteration):
                    next(self.guesser._type1_matches(params[0]))

    def test__type2_matches(self):
        """Test _type2_matches()."""
        for params in self.type2_set:
            with self.subTest(string=params[0]):
                self.assertEqual(next(self.guesser._type2_matches(params[0])), params[1])

        for params in self.nonsense_set:
            with self.subTest(string=params[0]):
                with self.assertRaises(StopIteration):
                    next(self.guesser._type2_matches(params[0]))

    def test__type3_matches(self):
        """Test _type3_matches()."""
        for params in self.type3_set:
            with self.subTest(string=params[0]):
                self.assertEqual(next(self.guesser._type3_matches(params[0])), params[1])

        for params in self.nonsense_set:
            with self.subTest(string=params[0]):
                with self.assertRaises(StopIteration):
                    next(self.guesser._type2_matches(params[0]))

    def test_guess(self):
        """Test the guess() method."""
        param_sets = chain(self.type1_set,
                           self.type2_set,
                           self.type3_set,
                           self.nonsense_set)

        for params in param_sets:
            with self.subTest(string=params[0]):
                self.assertEqual(self.guesser.guess(params[0]), params[1])


