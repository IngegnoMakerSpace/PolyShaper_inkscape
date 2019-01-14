#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Border-related classes and functions tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from inkex import etree # pylint: disable=import-error
from polyshaper.border import Border, BorderPainter # pylint: disable=import-error,no-name-in-module
from polyshaper.workingarea import WorkingAreaGenerator # pylint: disable=import-error,no-name-in-module

class BorderTest(unittest.TestCase):
    """ Tests for border class
    """

    def test_build_border_with_no_path(self):
        """ Tests that Border instance is correctly built when no path is present
        """

        border = Border([], 10)

        self.assertEqual(border.width(), 0)
        self.assertEqual(border.height(), 0)
        self.assertEqual(border.left(), 0)
        self.assertEqual(border.right(), 0)
        self.assertEqual(border.top(), 0)
        self.assertEqual(border.bottom(), 0)

    def test_build_border_with_one_path_one_point(self): # pylint: disable=invalid-name
        """ Tests that Border instance is correctly built when one path with one point is present
        """

        border = Border([[(10, 20)]], 10)

        self.assertEqual(border.width(), 20)
        self.assertEqual(border.height(), 20)
        self.assertEqual(border.left(), 0)
        self.assertEqual(border.right(), 20)
        self.assertEqual(border.top(), 30)
        self.assertEqual(border.bottom(), 10)

    def test_build_border_with_empty_path(self): # pylint: disable=invalid-name
        """ Tests that Border instance is correctly built when no path is present
        """

        border = Border([[]], 10)

        self.assertEqual(border.width(), 0)
        self.assertEqual(border.height(), 0)
        self.assertEqual(border.left(), 0)
        self.assertEqual(border.right(), 0)
        self.assertEqual(border.top(), 0)
        self.assertEqual(border.bottom(), 0)

    def test_build_border_with_one_path(self):
        """ Tests that Border instance is correctly build when one path is present
        """

        border = Border([[(30, 15), (20, 20), (25, 40)]], 10)

        self.assertEqual(border.width(), 30)
        self.assertEqual(border.height(), 45)
        self.assertEqual(border.left(), 10)
        self.assertEqual(border.right(), 40)
        self.assertEqual(border.top(), 50)
        self.assertEqual(border.bottom(), 5)

    def test_build_border_with_multiple_paths(self): # pylint: disable=invalid-name
        """ Tests that Border instance is correctly build when multiple paths are present
        """

        border = Border([[(30, 15), (20, 20), (25, 40)], [(90, 30), (30, 90)]], 10)

        self.assertEqual(border.width(), 90)
        self.assertEqual(border.height(), 95)
        self.assertEqual(border.left(), 10)
        self.assertEqual(border.right(), 100)
        self.assertEqual(border.top(), 100)
        self.assertEqual(border.bottom(), 5)

    def test_skip_empty_paths(self):
        """ Tests that empty paths are skipped
        """

        border = Border([[(30, 15), (20, 20), (25, 40)], [], [(90, 30), (30, 90)], []], 10)

        self.assertEqual(border.width(), 90)
        self.assertEqual(border.height(), 95)
        self.assertEqual(border.left(), 10)
        self.assertEqual(border.right(), 100)
        self.assertEqual(border.top(), 100)
        self.assertEqual(border.bottom(), 5)

    def test_skip_initial_path(self):
        """ Tests that an empty paths as the first path is skipped
        """

        border = Border([[], [(30, 15), (20, 20), (25, 40)], [(90, 30), (30, 90)]], 10)

        self.assertEqual(border.width(), 90)
        self.assertEqual(border.height(), 95)
        self.assertEqual(border.left(), 10)
        self.assertEqual(border.right(), 100)
        self.assertEqual(border.top(), 100)
        self.assertEqual(border.bottom(), 5)

    def test_border_vertices(self):
        """ Tests that Border reports its vertices correctly
        """

        border = Border([[(30, 15), (20, 20), (25, 40)]], 10)

        self.assertEqual(border.bottom_left(), (10, 5))
        self.assertEqual(border.bottom_right(), (40, 5))
        self.assertEqual(border.top_left(), (10, 50))
        self.assertEqual(border.top_right(), (40, 50))


class BorderPainterTest(unittest.TestCase):
    """ Tests for the BorderPainter class

    NOTE: to_uu here simply doubles its value
    """

    def setUp(self):
        """ Setup for tests
        """

        # The function to convert to user units. For tests we simply double the value
        self.to_uu = lambda x: 2 * x

    def test_do_not_draw_border_if_equal_working_area(self): # pylint: disable=invalid-name
        """ Tests that no border is drawn if border is coincident with the working area
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 300)

        root = etree.Element("root")
        generator.upsert(root)
        num_initial_root_children = len(root[0])

        border = Border([[(0, 0), (400, 300)]], 0)
        painter = BorderPainter(border)

        painter.paint(generator)

        self.assertEqual(len(root[0]), num_initial_root_children)

    def test_draw_border(self):
        """ Tests that the border is drawn if requested
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 300)

        root = etree.Element("root")
        generator.upsert(root)
        border_index = len(root[0]) # border is added at the end of the list of children

        border = Border([[(40, 20), (160, 200)]], 0)
        painter = BorderPainter(border)

        painter.paint(generator)

        self.assertEqual(root[0][border_index].tag, "rect")
        self.assertEqual(root[0][border_index].get("x"), "10.0")
        self.assertEqual(root[0][border_index].get("y"), "5.0")
        self.assertEqual(root[0][border_index].get("width"), "30.0")
        self.assertEqual(root[0][border_index].get("height"), "45.0")
        self.assertEqual(root[0][border_index].get("style"), ("stroke-width:0.0625;"
                                                              "stroke-miterlimit:4;"
                                                              "stroke-dasharray:0.25,0.25;"
                                                              "stroke-dashoffset:0;"
                                                              "fill:none"))
