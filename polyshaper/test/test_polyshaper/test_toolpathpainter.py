#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper tool path drawing tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from inkex import etree # pylint: disable=import-error
from polyshaper.toolpathpainter import ToolPathPainter # pylint: disable=import-error,no-name-in-module

class ToolPathPainterTest(unittest.TestCase):
    """ Tests for the class drawing the tool path
    """

    def test_path_is_not_added_when_empty(self): # pylint: disable=invalid-name
        """ Tests that the path is not added when empty
        """
        path = []
        painter = ToolPathPainter(path)
        root_element = etree.Element("root")
        factor = 100.0 / 300.0

        painter.paint(root_element, factor, "255,0,0")

        self.assertEqual(len(root_element), 0)

    def test_path_element_is_added(self):
        """ Tests that the path element is added
        """
        path = [(10, 10)]
        painter = ToolPathPainter(path)
        root_element = etree.Element("root")
        factor = 100.0 / 300.0

        painter.paint(root_element, factor, "255,0,0")

        self.assertEqual(root_element[0].tag, "path")

    def test_path_color(self):
        """ Tests that the correct color and width are added to the path
        """
        path = [(10, 10)]
        painter = ToolPathPainter(path)
        root_element = etree.Element("root")
        factor = 100.0 / 300.0

        painter.paint(root_element, factor, "255,0,0")

        self.assertEqual(root_element[0].get("style"), "stroke:rgb(255,0,0);fill:none")

    def test_path_coordinates(self):
        """ Tests that the coordinates of the path have the correct value
        """
        path = [(150, 75), (300, 0), (0, 150)]
        painter = ToolPathPainter(path)
        root_element = etree.Element("root")
        factor = 100.0 / 300.0

        painter.paint(root_element, factor, "255,0,0")

        self.assertEqual(root_element[0].get("d"),
                         "M 0.0,0.0 L 50.0,25.0 100.0,0.0 0.0,50.0")
