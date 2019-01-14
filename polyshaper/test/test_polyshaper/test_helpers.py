#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Helper functions and classes tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
import os
from polyshaper.helpers import squared_length, length, squared_distance, distance # pylint: disable=import-error,no-name-in-module
from polyshaper.helpers import verify_path_closed, point_path_squared_distance, rotate_closed_path # pylint: disable=import-error,no-name-in-module
from polyshaper.helpers import invert_transform, generate_path_svg # pylint: disable=import-error,no-name-in-module
from polyshaper.errors import InvalidCuttingPath # pylint: disable=import-error,no-name-in-module


class HelpersTest(unittest.TestCase):
    """ Tests for the helper functions and classes
    """

    # base_filename is not tested
    # write_file is not tested

    def test_squared_length(self):
        """ Tests the squared_length function for 2D vectors
        """

        self.assertAlmostEqual(squared_length((3.0, 4.0)), 25.0)

    def test_length(self):
        """ Tests the length function for 2D vectors
        """

        self.assertAlmostEqual(length((3.0, 4.0)), 5.0)

    def test_squared_distance(self):
        """ Tests the squared_distance function for 2D vectors
        """

        self.assertAlmostEqual(squared_distance((1.0, 7.0), (5.0, 4.0)), 25.0)

    def test_distance(self):
        """ Tests the distance function for 2D points
        """

        self.assertAlmostEqual(distance((1.0, 7.0), (5.0, 4.0)), 5.0)

    def test_verify_path_closed_with_open_path(self): # pylint: disable=invalid-name
        """ Tests that the verify_closed_path throws an exception for open paths
        """

        path = [(1, 2), (3, 4), (5, 6)]

        with self.assertRaises(InvalidCuttingPath) as context_manager:
            verify_path_closed(path, 0.1)

        exception = context_manager.exception
        self.assertEqual(exception.reason, "path is not closed")

    def test_verify_path_closed_with_closd_path(self): # pylint: disable=invalid-name,no-self-use
        """ Tests that the verify_closed_path does not throw an exception for closed paths
        """

        path = [(1, 2), (3, 4), (5, 6), (1, 2)]

        # If an exception is thrown the test will fail
        verify_path_closed([path], 0.1)

    def test_point_path_squared_distance_for_path_with_single_point(self): # pylint: disable=invalid-name
        """ Tests that point_path_squared_distance works with a path made up of a single point
        """

        point = (0, 0)
        path = [(3, 4)]

        (dist, idx) = point_path_squared_distance(point, path)

        self.assertAlmostEqual(dist, 25.0)
        self.assertEqual(idx, 0)

    def test_point_path_squared_distance(self): # pylint: disable=invalid-name
        """ Tests that the point_path_squared_distance function works as expected
        """

        point = (0, 0)
        path = [(1, 10), (7, 9), (3, 4), (-6, 2), (0, -98)]

        (dist, idx) = point_path_squared_distance(point, path)

        self.assertAlmostEqual(dist, 25.0)
        self.assertEqual(idx, 2)

    def test_rotate_closed_path_with_empty_path(self): # pylint: disable=invalid-name
        """ Tests that rotate_closed_path returns an empty path for empty paths
        """

        self.assertEqual(rotate_closed_path([], 10), [])

    def test_rotate_closed_path_with_0_new_start(self): # pylint: disable=invalid-name
        """ Tests that rotate_closed_path returns path if new_start is 0
        """

        path = [(1, 10), (7, 9), (3, 4), (-6, 2), (0, -98), (1, 10)]
        self.assertEqual(rotate_closed_path(path, 0), path)

    def test_rotate_closed_path_with_new_start_beyond_end(self): # pylint: disable=invalid-name
        """ Tests that rotate_closed_path returns path if new_start is over length of path
        """

        path = [(1, 10), (7, 9), (3, 4), (-6, 2), (0, -98), (1, 10)]
        self.assertEqual(rotate_closed_path(path, 100), path)

    def test_rotate_closed_path(self):
        """ Tests that rotate_closed_path returns
        """

        path = [(1, 10), (7, 9), (3, 4), (-6, 2), (0, -98), (1, 10)]
        new_start = 3
        expected_path = [(-6, 2), (0, -98), (1, 10), (7, 9), (3, 4), (-6, 2)]

        self.assertEqual(rotate_closed_path(path, new_start), expected_path)

    def test_invert_transform(self):
        """ Tests the invert_transform function

        The function is taken from inkscape version 0.92
        """

        mat = [
            [1., 3., 4.],
            [2., -2., 6.]
        ]
        expected_inv = [
            [0.25, 0.375, -3.25],
            [0.25, -0.125, -0.25]
        ]

        self.assertEqual(invert_transform(mat), expected_inv)

    def test_generate_path_svg(self):
        """ Tests the generate_path_svg function
        """

        class DummyPainter:
            def __init__(self):
                self.num_calls = 0
                self.parent_element = None
                self.factor = None
                self.color = None

            def paint(self, parent_element, factor, color):
                self.num_calls += 1
                self.parent_element = parent_element
                self.factor = factor
                self.color = color

        painter = DummyPainter()

        doc = generate_path_svg(painter)

        self.assertEqual(painter.num_calls, 1)
        self.assertEqual(painter.parent_element, doc.getroot())
        self.assertEqual(painter.factor, 1.0)
        self.assertEqual(painter.color, "0,0,0")

        self.assertEqual(doc.docinfo.xml_version, "1.0")
        self.assertEqual(doc.docinfo.standalone, False)
        self.assertEqual(doc.docinfo.doctype, '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
        self.assertEqual(doc.getroot().tag, "{http://www.w3.org/2000/svg}svg")
        self.assertEqual(doc.getroot().get("version"), "1.1")
