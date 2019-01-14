#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper svg paths extraction tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from inkex import etree # pylint: disable=import-error
import simplepath # pylint: disable=import-error
from polyshaper.pathsextraction import FlattenBezier, PathsExtractor # pylint: disable=import-error,no-name-in-module
from polyshaper.errors import UnrecognizedSVGElement # pylint: disable=import-error,no-name-in-module

class FlattenBezierTest(unittest.TestCase):
    """ Tests for the class discretizing beziers and arcs in SVG paths

    The class uses the inkscape library, so we have one test to check we get the expected result
    """

    def test_flatten_complex_path(self):
        """ Tests flattening of a complex svg path
        """

        original = ("M 31.75,246.35119 Q -103.17337,325.09171 -73.319959,35.128951 "
                    "30.994047,99.696429 64.916958,144.277 47.499406,119.14669 142.11905,128.42262 "
                    "c 125.15382,72.71094 28.37304,48.92858 30.23809,68.03571 "
                    "-127.361415,-31.73781 -47.32064,32.81825 -69.54762,49.89286 "
                    "-66.090829,61.27158 28.37765,33.34354 80.88691,28.72618 A 51.016859,153.05058 "
                    "0 1 0 100,100")

        flattened = ("M31.75 246.35119L-25.4131361875 262.677495062L-61.97917475 232.91589025"
                     "L-77.9481156875 157.066375563L-73.319959 35.128951L64.916958 144.277"
                     "L75.508705 127.74825L142.11905 128.42262L199.380746719 167.041187344"
                     "L203.47138375 182.54190375L172.35714 196.45833L110.885396484 188.46358375"
                     "L98.157916875 203.1001025L105.143143828 226.88895L102.80952 246.35119"
                     "L80.1819165156 277.337919687L98.777941625 285.4226325L183.69643 275.07737"
                     "L188.045578834 122.576600131L171.030193349 61.983637335L146.195362269 "
                     "35.0337282295L120.196244292 48.9488233654L100.0 100.0")

        flatten_bezier = FlattenBezier(10.0)

        expected = simplepath.parsePath(flattened)
        result = flatten_bezier(original)

        self.assertEqual(len(result), len(expected))
        for (res, expect) in zip(result, expected):
            self.assertEqual(len(res), 2)
            self.assertEqual(len(expect), 2)

            self.assertEqual(res[0], expect[0])

            self.assertEqual(len(res[1]), len(expect[1]))
            for (resv, expectv) in zip(res[1], expect[1]):
                self.assertAlmostEqual(resv, expectv)

    def test_failure_empty_curve(self):
        """ Tests fix to a bug with empty input curves
        """

        flatten_bezier = FlattenBezier(10.0)
        self.assertEqual(flatten_bezier(""), [])


def to_mm(value):
    """ The function to convert to millimeters. For tests the identity function is enough
    """

    return value


class PathsExtractorTest(unittest.TestCase):
    """ Tests for the class extracting tool paths from svg elements
    """

    def test_get_elements(self):
        """ Tests that elements passed to the constructor are used
        """

        root = etree.Element("root")
        element1 = etree.SubElement(root, "path")
        element2 = etree.SubElement(root, "rect")

        extractor = PathsExtractor([element1, element2], to_mm, "wId")

        self.assertEqual(extractor.get_elements(), [element1, element2])


    def test_remove_working_area(self):
        """ Tests that the working area is not considered among svg elements to use
        """

        root = etree.Element("root")
        working_area = etree.SubElement(root, "svg", {"id": "wId"})
        other_element = etree.SubElement(root, "path")

        extractor = PathsExtractor([working_area, other_element], to_mm, "wId")

        self.assertEqual(extractor.get_elements(), [other_element])

    def test_throw_exception_for_unrecognized_svg_element(self): #pylint: disable=invalid-name
        """ Tests that an exception is thrown for unrecognized svg elements
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "invalidElement")

        extractor = PathsExtractor([element], to_mm, "wId")

        with self.assertRaises(UnrecognizedSVGElement) as context_manager:
            extractor.extract()

        exception = context_manager.exception
        self.assertEqual(exception.element, "invalidElement")

    def test_extract_svg_path_with_only_straight_lines(self): #pylint: disable=invalid-name
        """ Tests that svg paths are correctly extracted
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': "M 70,800 l 125,-300 l 60,490"})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 1)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0)])

    def test_extract_multiple_paths_when_lines_interrupted(self): #pylint: disable=invalid-name
        """ Tests that multiple paths are generated when svg path is not continuos
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': "M 70,800 l 125,-300 l 60,490 M 100,100 L 200,200"})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 2)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0)])
        self.assertEqual(extractor.paths()[1], [(100.0, 100.0), (200.0, 200.0)])

    def test_extract_path_inside_groups(self): #pylint: disable=invalid-name
        """ Tests that a path inside a group is correctly extracted
        """

        root = etree.Element("root")
        group = etree.SubElement(root, "{http://www.w3.org/2000/svg}g")
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 70,800 l 125,-300 l 60,490"})

        extractor = PathsExtractor([group], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 1)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0)])

    def test_extract_paths_inside_groups(self): #pylint: disable=invalid-name
        """ Tests that paths inside groups are correctly extracted
        """

        root = etree.Element("root")
        group = etree.SubElement(root, "{http://www.w3.org/2000/svg}g")
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 70,800 l 125,-300 l 60,490"})
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 60,700 l 127,-500 l 70,900"})

        extractor = PathsExtractor([group], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 2)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0)])
        self.assertEqual(extractor.paths()[1], [(60.0, 700.0), (187.0, 200.0), (257.0, 1100.0)])

    def test_extract_paths_inside_groups_and_outside(self): #pylint: disable=invalid-name
        """ Tests that a mix of paths inside groups and outside are correctly extracted
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': "M 70,800 l 125,-300 l 60,390"})
        group = etree.SubElement(root, "{http://www.w3.org/2000/svg}g")
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 70,800 l 125,-300 l 60,490"})
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 60,700 l 127,-500 l 70,900"})

        extractor = PathsExtractor([element, group], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 3)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 890.0)])
        self.assertEqual(extractor.paths()[1], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0)])
        self.assertEqual(extractor.paths()[2], [(60.0, 700.0), (187.0, 200.0), (257.0, 1100.0)])

    def test_extract_paths_inside_group_keeping_transform(self): #pylint: disable=invalid-name
        """ Tests that extracted path from a group take the transformation into account
        """

        root = etree.Element("root")
        group = etree.SubElement(root, "{http://www.w3.org/2000/svg}g",
                                 {'transform': "matrix(1,2,3,4,5,6)"})
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 10,20 L 50,30 L 20,70"})

        extractor = PathsExtractor([group], to_mm, "wId")
        extractor.extract()

        self.assertEqual(extractor.paths()[0], [(75.0, 106.0), (145.0, 226.0), (235.0, 326.0)])

    def test_extract_paths_keeping_transform(self): #pylint: disable=invalid-name
        """ Tests that extracted path from a group take the transformation into account
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'transform': "matrix(1,2,3,4,5,6)",
                                    'd': "M 10,20 L 50,30 L 20,70"})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(extractor.paths()[0], [(75.0, 106.0), (145.0, 226.0), (235.0, 326.0)])

    def test_extract_paths_inside_group_keeping_nested_transform(self): #pylint: disable=invalid-name
        """ Tests that extracted path from elements with nested transformation works correctly
        """

        root = etree.Element("root")
        group = etree.SubElement(root, "{http://www.w3.org/2000/svg}g",
                                 {'transform': "translate(10,20)"})
        subgroup = etree.SubElement(group, "{http://www.w3.org/2000/svg}g",
                                    {'transform': "matrix(1,2,3,4,5,6)"})
        etree.SubElement(subgroup, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 10,20 L 50,30 L 20,70"})

        extractor = PathsExtractor([group], to_mm, "wId")
        extractor.extract()

        self.assertEqual(extractor.paths()[0], [(85.0, 126.0), (155.0, 246.0), (245.0, 346.0)])

    def test_closed_paths(self):
        """ Tests that closed paths are extracted correctly by repeating the first point at the end
        """

        root = etree.Element("root")
        group = etree.SubElement(root, "{http://www.w3.org/2000/svg}g")
        etree.SubElement(group, "{http://www.w3.org/2000/svg}path",
                         {'d': "M 70,800 l 125,-300 l 60,490 Z"})

        extractor = PathsExtractor([group], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 1)
        self.assertEqual(extractor.paths()[0],
                         [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0), (70.0, 800.0)])

    def test_closed_paths_with_multiple_paths(self): #pylint: disable=invalid-name
        """ Tests that closed paths are extracted correctly also when multiple subpaths are present
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': "M 70,800 l 125,-300 l 60,490 Z M 100,100 L 200,200"})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 2)
        self.assertEqual(extractor.paths()[0],
                         [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0), (70.0, 800.0)])
        self.assertEqual(extractor.paths()[1], [(100.0, 100.0), (200.0, 200.0)])

    def test_flatten_path_if_requested(self):
        """ Tests that path is flattened if the constructor flatten parameter is not None
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': "dummy value to check"})

        class FlattenMock: #pylint: disable=missing-docstring,too-few-public-methods
            def __init__(self, test):
                self.test = test
            def __call__(self, curve): #pylint: disable=missing-docstring
                self.test.assertEqual(curve, "dummy value to check")

                return [('M', (70.0, 800.0)), ('L', (195.0, 500.0)), ('L', (255.0, 990.0))]

        extractor = PathsExtractor([element], to_mm, "wId", FlattenMock(self))
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 1)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0)])

    def test_use_parent_transform_for_single_path(self): #pylint: disable=invalid-name
        """ Tests that extracted path takes the parent transformation into account
        """

        root = etree.Element("root", {'transform': "translate(10,20)"})
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'transform': "matrix(1,2,3,4,5,6)",
                                    'd': "M 10,20 L 50,30 L 20,70"})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(extractor.paths()[0], [(85.0, 126.0), (155.0, 246.0), (245.0, 346.0)])

    def test_use_parent_transform_for_single_path_with_multiple_parents(self): #pylint: disable=invalid-name
        """ Tests that extracted path takes all the ancestors transformations into account
        """

        root = etree.Element("root", {'transform': "scale(10)"})
        parent = etree.SubElement(root, "{http://www.w3.org/2000/svg}g",
                                  {'transform': "translate(10,20)"})
        element = etree.SubElement(parent, "{http://www.w3.org/2000/svg}path",
                                   {'transform': "matrix(1,2,3,4,5,6)",
                                    'd': "M 10,20 L 50,30 L 20,70"})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(extractor.paths()[0],
                         [(850.0, 1260.0), (1550.0, 2460.0), (2450.0, 3460.0)])

    def test_use_parent_transform_for_multiple_path(self): #pylint: disable=invalid-name
        """ Tests that extracted path takes the parent transformation into account
        """

        root1 = etree.Element("root", {'transform': "translate(10,20)"})
        element1 = etree.SubElement(root1, "{http://www.w3.org/2000/svg}path",
                                    {'transform': "matrix(1,2,3,4,5,6)",
                                     'd': "M 10,20 L 50,30 L 20,70"})
        root2 = etree.Element("root", {'transform': "translate(5,10)"})
        element2 = etree.SubElement(root2, "{http://www.w3.org/2000/svg}path",
                                    {'transform': "matrix(1,2,3,4,5,6)",
                                     'd': "M 10,20 L 50,30 L 20,70"})

        extractor = PathsExtractor([element1, element2], to_mm, "wId")
        extractor.extract()

        self.assertEqual(extractor.paths()[0], [(85.0, 126.0), (155.0, 246.0), (245.0, 346.0)])
        self.assertEqual(extractor.paths()[1], [(80.0, 116.0), (150.0, 236.0), (240.0, 336.0)])

    def test_automatically_close_open_paths_does_nothing_if_paths_closed(self): #pylint: disable=invalid-name
        """ Tests that nothing changes if closing paths is requested but paths are closed
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': ("M 70,800 l 125,-300 l 60,490 Z "
                                          "M 100,100 L 200,200 L 100,100")})

        extractor = PathsExtractor([element], to_mm, "wId")
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 2)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0),
                                                (70.0, 800.0)])
        self.assertEqual(extractor.paths()[1], [(100.0, 100.0), (200.0, 200.0), (100.0, 100.0)])

    def test_automatically_close_open_paths(self): #pylint: disable=invalid-name
        """ Tests that open paths are automatically closed if requested
        """

        root = etree.Element("root")
        element = etree.SubElement(root, "{http://www.w3.org/2000/svg}path",
                                   {'d': "M 70,800 l 125,-300 l 60,490 M 100,100 L 200,200"})

        extractor = PathsExtractor([element], to_mm, "wId", auto_close_path=True)
        extractor.extract()

        self.assertEqual(len(extractor.paths()), 2)
        self.assertEqual(extractor.paths()[0], [(70.0, 800.0), (195.0, 500.0), (255.0, 990.0),
                                                (70.0, 800.0)])
        self.assertEqual(extractor.paths()[1], [(100.0, 100.0), (200.0, 200.0), (100.0, 100.0)])
