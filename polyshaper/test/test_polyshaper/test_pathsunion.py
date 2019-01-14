#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper union of closed paths tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from polyshaper.pathsunion import PathsJoiner # pylint: disable=import-error,no-name-in-module
from polyshaper.errors import InvalidCuttingPath # pylint: disable=import-error,no-name-in-module

class PathsJoinerTest(unittest.TestCase):
    """ Tests for the class joining closed paths
    """

    def test_empty_path_for_no_paths(self):
        """ Tests that when an empty list of path is provided, an emtpy path is returned
        """

        joiner = PathsJoiner([], 1.0)
        joiner.unite()

        self.assertEqual(joiner.union_path(), [])

    def test_path_is_returned_if_one_path_is_provided(self): # pylint: disable=invalid-name
        """ Tests that when one path is provided, the same path is returned
        """

        path = [(1, 2), (3, 4), (5, 6), (1, 2)]

        joiner = PathsJoiner([path], 1.0)
        joiner.unite()

        self.assertEqual(joiner.union_path(), path)

    def test_exception_thrown_for_non_closed_paths(self): # pylint: disable=invalid-name
        """ Tests that an exception is thrown for non-closed paths
        """

        path = [(1, 2), (3, 4), (5, 6)]

        with self.assertRaises(InvalidCuttingPath) as context_manager:
            PathsJoiner([path], 0.1)

        exception = context_manager.exception
        self.assertEqual(exception.reason, "path is not closed")

    def test_union_of_paths_made_up_of_single_point(self): # pylint: disable=invalid-name
        """ Tests that two paths made up of a single point each are correctly joined
        """

        path1 = [(1, 2)]
        path2 = [(3, 4)]
        expected_union = [(1, 2), (3, 4), (1, 2)]

        joiner = PathsJoiner([path1, path2], 0.1)
        joiner.unite()

        self.assertEqual(joiner.union_path(), expected_union)

    def test_union_of_point_and_path(self):
        """ Tests that a single point and a path are correctly joined
        """

        path1 = [(0, 0)]
        path2 = [(2, 2), (1, 1), (1, 2), (2, 2)]
        expected_union = [(0, 0), (1, 1), (1, 2), (2, 2), (1, 1), (0, 0)]

        joiner = PathsJoiner([path1, path2], 0.1)
        joiner.unite()

        self.assertEqual(joiner.union_path(), expected_union)

    def test_union_of_two_paths(self):
        """ Tests that two paths are correctly joined
        """

        path1 = [(-1, -1), (0, 0), (-1, 0), (-1, -1)]
        path2 = [(2, 2), (1, 1), (1, 2), (2, 2)]
        expected_union = [(-1, -1), (0, 0), (1, 1), (1, 2), (2, 2), (1, 1), (0, 0), (-1, 0),
                          (-1, -1)]

        joiner = PathsJoiner([path1, path2], 0.1)
        joiner.unite()

        self.assertEqual(joiner.union_path(), expected_union)

    def test_union_of_three_paths(self):
        """ Tests that three paths are correctly joined
        """

        path1 = [(-1, -1), (0, 0), (-1, 0), (-1, -1)]
        path2 = [(0, 2), (-1, 3), (-1, 2), (0, 2)]
        path3 = [(2, 2), (1, 1), (1, 2), (2, 2)]
        expected_union = [(-1, -1), (0, 0), (1, 1), (1, 2), (0, 2), (-1, 3), (-1, 2), (0, 2),
                          (1, 2), (2, 2), (1, 1), (0, 0), (-1, 0), (-1, -1)]

        joiner = PathsJoiner([path1, path2, path3], 0.1)
        joiner.unite()

        self.assertEqual(joiner.union_path(), expected_union)
