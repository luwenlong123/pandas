import nose

import pandas as pd
from pandas import DataFrame, ordered_merge
from pandas.util import testing as tm
from pandas.util.testing import assert_frame_equal

from numpy import nan


class TestOrderedMerge(tm.TestCase):

    def setUp(self):
        self.left = DataFrame({'key': ['a', 'c', 'e'],
                               'lvalue': [1, 2., 3]})

        self.right = DataFrame({'key': ['b', 'c', 'd', 'f'],
                                'rvalue': [1, 2, 3., 4]})

    # GH #813

    def test_basic(self):
        result = ordered_merge(self.left, self.right, on='key')
        expected = DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f'],
                              'lvalue': [1, nan, 2, nan, 3, nan],
                              'rvalue': [nan, 1, 2, 3, nan, 4]})

        assert_frame_equal(result, expected)

    def test_ffill(self):
        result = ordered_merge(
            self.left, self.right, on='key', fill_method='ffill')
        expected = DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f'],
                              'lvalue': [1., 1, 2, 2, 3, 3.],
                              'rvalue': [nan, 1, 2, 3, 3, 4]})
        assert_frame_equal(result, expected)

    def test_multigroup(self):
        left = pd.concat([self.left, self.left], ignore_index=True)
        # right = concat([self.right, self.right], ignore_index=True)

        left['group'] = ['a'] * 3 + ['b'] * 3
        # right['group'] = ['a'] * 4 + ['b'] * 4

        result = ordered_merge(left, self.right, on='key', left_by='group',
                               fill_method='ffill')
        expected = DataFrame({'key': ['a', 'b', 'c', 'd', 'e', 'f'] * 2,
                              'lvalue': [1., 1, 2, 2, 3, 3.] * 2,
                              'rvalue': [nan, 1, 2, 3, 3, 4] * 2})
        expected['group'] = ['a'] * 6 + ['b'] * 6

        assert_frame_equal(result, expected.ix[:, result.columns])

        result2 = ordered_merge(self.right, left, on='key', right_by='group',
                                fill_method='ffill')
        assert_frame_equal(result, result2.ix[:, result.columns])

        result = ordered_merge(left, self.right, on='key', left_by='group')
        self.assertTrue(result['group'].notnull().all())

    def test_merge_type(self):
        class NotADataFrame(DataFrame):

            @property
            def _constructor(self):
                return NotADataFrame

        nad = NotADataFrame(self.left)
        result = nad.merge(self.right, on='key')

        tm.assertIsInstance(result, NotADataFrame)

    def test_empty_sequence_concat(self):
        # GH 9157
        empty_pat = "[Nn]o objects"
        none_pat = "objects.*None"
        test_cases = [
            ((), empty_pat),
            ([], empty_pat),
            ({}, empty_pat),
            ([None], none_pat),
            ([None, None], none_pat)
        ]
        for df_seq, pattern in test_cases:
            tm.assertRaisesRegexp(ValueError, pattern, pd.concat, df_seq)

        pd.concat([pd.DataFrame()])
        pd.concat([None, pd.DataFrame()])
        pd.concat([pd.DataFrame(), None])

if __name__ == '__main__':
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)
