#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper working area generation tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from inkex import etree # pylint: disable=import-error
from polyshaper.workingarea import WorkingAreaGenerator # pylint: disable=import-error,no-name-in-module

class WorkingAreaGeneratorTest(unittest.TestCase):
    """ Tests for the class generating the working area

    NOTE: to_uu here simply doubles its value
    """

    def setUp(self):
        """ Setup for tests
        """

        # The function to convert to user units. For tests we simply double the value
        self.to_uu = lambda x: 2 * x

    def test_upsert_adds_working_area_group(self): # pylint: disable=invalid-name
        """ Tests that the upsert function inserts the working area with the correct id
        """
        generator = WorkingAreaGenerator(self.to_uu, "wId")
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0].tag, "svg")
        self.assertEqual(root[0].get("id"), "wId")

    def test_upsert_does_not_create_duplicated_working_area(self): # pylint: disable=invalid-name
        """ Tests that upsert does not insert a new working area if it is already present
        """
        generator = WorkingAreaGenerator(self.to_uu, "wId")
        root = etree.Element("root")
        etree.SubElement(root, "svg", {"id": "wId"})

        generator.upsert(root)

        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "svg")
        self.assertEqual(root[0].get("id"), "wId")

    def test_add_working_area_style(self):
        """ Test that the added working area has the correct style
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0].get("style"),
                         "fill:none;stroke-width:0.25;stroke:rgb(0,0,0)")

    def test_add_working_area_size(self):
        """ Tests that the added working area has the correct size
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(1323, 876)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0].get("width"), "2646.0")
        self.assertEqual(root[0].get("height"), "1752.0")

    def test_add_working_area_position(self):
        """ Tests that the added working area has the correct position
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(1323, 876)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0].get("x"), "0.0")
        self.assertEqual(root[0].get("y"), "0.0")

    def test_add_working_area_view_box_and_scaling_policy(self): # pylint: disable=invalid-name
        """ Tests that the added working area has the correct viewBox and scaling policy
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(500, 500)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0].get("viewBox"), "0 0 100 100.0")
        self.assertEqual(root[0].get("preserveAspectRatio"), "none")

    def test_add_working_area_view_box_rectangular_area(self): # pylint: disable=invalid-name
        """ Tests that the added working area has the correct viewBox in case of rectangular areas
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(500, 400)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0].get("viewBox"), "0 0 100 80.0")


    def test_add_the_rectangle(self):
        """ Tests that a rectangle is added
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 300)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0][0].tag, "rect")
        self.assertEqual(root[0][0].get("x"), "0")
        self.assertEqual(root[0][0].get("y"), "0")
        self.assertEqual(root[0][0].get("width"), "100")
        self.assertEqual(root[0][0].get("height"), "75.0")

    def test_add_cross(self):
        """ Tests that a cross is added
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 200)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0][1].tag, "path")
        self.assertEqual(root[0][1].get("d"), "M -2.5,0 L 2.5,0 M 0,-2.5 L 0,2.5")

    def test_add_origin_coordinates_text(self): # pylint: disable=invalid-name
        """ Tests that coordinates at the orgin are added
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 200)
        root = etree.Element("root")

        generator.upsert(root)

        self.assertEqual(root[0][2].tag, "text")
        self.assertEqual(root[0][2].get("x"), "-7.0")
        self.assertEqual(root[0][2].get("y"), "-2.5")
        self.assertEqual(root[0][2].get("font-family"), "Verdana")
        self.assertEqual(root[0][2].get("font-size"), "2.5")
        self.assertEqual(root[0][2].text, "(0, 0)")

    def test_use_translate_transform(self):
        """ Tests that the transformation of the element is taken into account when a translation
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 200)
        root = etree.Element("root", {'transform': "translate(10,-30)"})

        generator.upsert(root)

        self.assertEqual(root[0].get("x"), "-20.0")
        self.assertEqual(root[0].get("y"), "60.0")

    def test_use_transform(self):
        """ Tests that the transformation of the element is taken into account
        """

        generator = WorkingAreaGenerator(self.to_uu, "wId")
        generator.set_size(400, 200)
        root = etree.Element("root", {'transform': "matrix(2, 0, 0, 1, 10,-30)"})

        generator.upsert(root)

        self.assertEqual(root[0].get("x"), "-10.0")
        self.assertEqual(root[0].get("y"), "60.0")
