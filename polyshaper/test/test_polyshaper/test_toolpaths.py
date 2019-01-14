#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper tool paths generation tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
import math
from polyshaper.toolpaths import EngravingToolPathsGenerator, discretize_path # pylint: disable=import-error,no-name-in-module
from polyshaper.toolpaths import CuttingToolPathsGenerator # pylint: disable=import-error,no-name-in-module
from polyshaper.errors import InvalidCuttingPath # pylint: disable=import-error,no-name-in-module
from polyshaper.border import Border # pylint: disable=import-error,no-name-in-module

class EngravingToolPathsGeneratorTest(unittest.TestCase): # pylint: disable=too-many-public-methods
    """ Tests for the class generating tool paths for the engraving machine
    """

    def assert_equal_paths(self, actual, expected):
        """ Asserts that two paths are equal

        This uses assertEqual for coordinates and assertAlmostEqual for angles
        """

        self.assertEqual(len(actual), len(expected))
        for (actual_point, expected_point) in zip(actual, expected):
            self.assertEqual(len(actual_point), len(expected_point))
            for (actual_value, expected_value) in zip(actual_point, expected_point):
                self.assertAlmostEqual(actual_value, expected_value)

    def test_return_empty_list_of_paths_if_no_path_is_provided(self): #pylint: disable=invalid-name
        """ Tests that an empty list of paths is returned when no input path is provided
        """

        generator = EngravingToolPathsGenerator([], 2, 0.00001, float('inf'))
        generator.generate()

        self.assertEqual(len(generator.paths()), 0)

    def test_number_of_tool_paths_equals_that_of_input_paths(self): #pylint: disable=invalid-name
        """ Tests that the number of returned tool paths is equal to the number of input paths
        """

        # Three input paths
        generator = EngravingToolPathsGenerator([[], [], []], 3, 0.00001, float('inf'))
        generator.generate()

        self.assertEqual(len(generator.paths()), 3)

    def test_single_point_paths_are_returned_with_angle_0(self): #pylint: disable=invalid-name
        """ Tests that when paths with a single point are provided, tool path have angle equal to 0
        """

        generator = EngravingToolPathsGenerator([[(1, 1)], [(7, 13)]], 5, 0.00001, float('inf'))
        generator.generate()

        self.assertEqual(generator.paths(), [[(1, 1, 5, 0)], [(7, 13, 5, 0)]])

    def test_horizontal_paths_with_two_points_correct_angle(self): #pylint: disable=invalid-name
        """ Tests that the correct angle is computed in case of horizontal paths with two points
        """

        hpath = [(10, 10), (50, 10)]
        hpath_reverse = [(60, 30), (20, 30)]
        generator = EngravingToolPathsGenerator([hpath, hpath_reverse], 7, 0.00001, float('inf'))
        generator.generate()

        self.assertAlmostEqual(generator.paths()[0][0][3], math.pi/2.0)
        self.assertAlmostEqual(generator.paths()[0][1][3], math.pi/2.0)
        self.assertAlmostEqual(generator.paths()[1][0][3], math.pi/2.0)
        self.assertAlmostEqual(generator.paths()[1][1][3], math.pi/2.0)

    def test_vertical_paths_with_two_points_correct_angle(self): #pylint: disable=invalid-name
        """ Tests that the correct angle is computed in case o vertical paths with two points
        """

        vpath = [(10, 10), (10, 50)]
        vpath_reverse = [(30, 60), (30, 20)]
        generator = EngravingToolPathsGenerator([vpath, vpath_reverse], 11, 0.00001, float('inf'))
        generator.generate()

        self.assertAlmostEqual(generator.paths()[0][0][3], 0)
        self.assertAlmostEqual(generator.paths()[0][1][3], 0)
        self.assertAlmostEqual(generator.paths()[1][0][3], 0)
        self.assertAlmostEqual(generator.paths()[1][1][3], 0)

    def test_paths_with_two_points_correct_angle(self): #pylint: disable=invalid-name
        """ Tests that the correct angle is computed in case o vertical paths with two points
        """

        path = [(10, 10), (50, 50)]
        path_reverse = [(30, 60), (25, 20)]
        generator = EngravingToolPathsGenerator([path, path_reverse], 13, 0.00001, float('inf'))
        generator.generate()

        self.assertAlmostEqual(generator.paths()[0][0][3], 3*math.pi/4)
        self.assertAlmostEqual(generator.paths()[0][1][3], 3*math.pi/4)
        self.assertAlmostEqual(generator.paths()[1][0][3], 3.01723765904)
        self.assertAlmostEqual(generator.paths()[1][1][3], 3.01723765904)

    def test_generic_path(self):
        """ Tests that the expected tool path is generated from a path
        """

        path = [(10, 10), (40, 40), (80, 40), (0, 70), (0, 0)]
        generator = EngravingToolPathsGenerator([path], 17, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [
            (10, 10, 17, 3*math.pi/4),
            (40, 40, 17, math.pi/2),
            (80, 40, 17, math.pi + 1.2120256565243244),
            (0, 70, 17, 2.0*math.pi),
            (0, 0, 17, 2.0*math.pi)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_skip_subsequent_coincident_points(self): #pylint: disable=invalid-name
        """ Tests that subsequent coincident points are merged into one
        """

        path = [(10, 10), (30, 50), (30, 50), (50, 70)]
        generator = EngravingToolPathsGenerator([path], 19, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [
            (10, 10, 19, 2.677945044588987),
            (30, 50, 19, 3*math.pi/4),
            (50, 70, 19, 3*math.pi/4)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_do_not_skip_entire_sequences_of_near_points(self): #pylint: disable=invalid-name
        """ Tests that long sequences of near points are not all skipped

        This is to ensure that if three subsequent points are near, but the first and the last are
        distant enough, the entire sequence is not skipped and only the central point is removed
        """

        path = [(0, 0), (2*0.00001/3, 0), (4*0.00001/3, 0), (10, 0)]
        generator = EngravingToolPathsGenerator([path], 23, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [
            (0, 0, 23, math.pi/2),
            (4*0.00001/3, 0, 23, math.pi/2),
            (10, 0, 23, math.pi/2)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_return_one_point_for_paths_of_two_near_points(self): #pylint: disable=invalid-name
        """ Tests that an input path with two near points generates a path with only one point
        """

        path = [(0, 0), (2*0.00001/3, 0)]
        generator = EngravingToolPathsGenerator([path], 29, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [(0, 0, 29, 0)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_return_one_point_for_paths_of_three_near_points(self): #pylint: disable=invalid-name
        """ Tests that an input path with three near points generates a path with only one point
        """

        path = [(0, 0), (0.00001/3, 0), (2*0.00001/3, 0)]
        generator = EngravingToolPathsGenerator([path], 31, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [(0, 0, 31, 0)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_rotation_on_the_right_side_anticlockwise(self): #pylint: disable=invalid-name
        """ Test that the tool rotates in the correct direction

        This is an anticlockwise path
        """

        path = [(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]
        generator = EngravingToolPathsGenerator([path], 37, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [
            (0, 0, 37, math.pi/2.0),
            (100, 0, 37, math.pi),
            (100, 100, 37, 3.0*math.pi/2.0),
            (0, 100, 37, 2.0*math.pi),
            (0, 0, 37, 2.0*math.pi)]

        self.assert_equal_paths(tool_path, expected_path)


    def test_rotation_on_the_right_side_clockwise(self): #pylint: disable=invalid-name
        """ Test that the tool rotates in the correct direction

        This is a clockwise path
        """

        path = [(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]
        generator = EngravingToolPathsGenerator([path], 41, 0.00001, float('inf'))
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [
            (0, 0, 41, 0.0),
            (0, 100, 41, -math.pi/2.0),
            (100, 100, 41, -math.pi),
            (100, 0, 41, -3.0*math.pi/2.0),
            (0, 0, 41, -3.0*math.pi/2.0)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_discretization(self):
        """ Tests that discretization is performed when requested
        """

        path = [(0, 0), (5, 5), (6, 5), (11, 5)]
        generator = EngravingToolPathsGenerator([path], 43, 0.00001, 2)
        generator.generate()

        tool_path = generator.paths()[0]
        expected_path = [
            (0, 0, 43, 3*math.pi/4),
            (1.25, 1.25, 43, 3*math.pi/4),
            (2.5, 2.5, 43, 3*math.pi/4),
            (3.75, 3.75, 43, 3*math.pi/4),
            (5, 5, 43, math.pi/2),
            (6, 5, 43, math.pi/2),
            (7.66666666666666, 5, 43, math.pi/2),
            (9.33333333333333, 5, 43, math.pi/2),
            (11, 5, 43, math.pi/2)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_wrong_rotations_with_discretized_c_letter(self): #pylint: disable=invalid-name
        """ Tests that the correct path is generated for a discretized "c"
        """

        path = [(19.029526753409453, 46.932526776777536),
                (19.029526753409453, 53.27957191013624),
                (16.56828763784405, 59.626617043494974),
                (11.645809688935472, 59.626617043494974),
                (6.723331740026893, 53.27957191013624),
                (4.262092624461493, 46.932526776777536),
                (1.8008537628960923, 34.23843933228227),
                (1.8008537628960923, 21.54434906556486),
                (4.262092624461493, 8.850236221069622),
                (9.184570855592293, 2.503199554377545),
                (16.56828763784405, 2.503199554377545),
                (23.952006113429142, 15.197303932206125),
                (28.87448293344883, 34.23843933228227)]
        generator = EngravingToolPathsGenerator([path], 5, 0.00001, 2)
        generator.generate()

        tool_path = generator.paths()[0]

        expected_path = [(19.029526753409453, 46.932526776777536, 5, 0.0),
                         (19.029526753409453, 48.51928806011721, 5, 0.0),
                         (19.029526753409453, 50.10604934345689, 5, 0.0),
                         (19.029526753409453, 51.692810626796565, 5, 0.0),
                         (19.029526753409453, 53.27957191013624, 5, 0.3699252394183272),
                         (18.4142169745181, 54.866333193475924, 5, 0.36992523941832545),
                         (17.798907195626754, 56.45309447681561, 5, 0.3699252394183272),
                         (17.183597416735402, 58.03985576015529, 5, 0.3699252394183272),
                         (16.56828763784405, 59.626617043494974, 5, 1.5707963267948966),
                         (14.927461654874525, 59.626617043494974, 5, 1.5707963267948966),
                         (13.286635671904998, 59.626617043494974, 5, 1.5707963267948966),
                         (11.645809688935472, 59.626617043494974, 5, 2.4819363952998965),
                         (10.661314099153756, 58.35720801682323, 5, 2.4819363952998965),
                         (9.67681850937204, 57.087798990151484, 5, 2.481936395299899),
                         (8.692322919590325, 55.81838996347973, 5, 2.4819363952998965),
                         (7.707827329808609, 54.548980936807986, 5, 2.4819363952998965),
                         (6.723331740026893, 53.27957191013624, 5, 2.771667414171465),
                         (6.1080219611355435, 51.692810626796565, 5, 2.7716674141714646),
                         (5.492712182244193, 50.10604934345689, 5, 2.7716674141714646),
                         (4.877402403352843, 48.51928806011721, 5, 2.771667414171465),
                         (4.262092624461493, 46.932526776777536, 5, 2.9500802850138443),
                         (3.910487072809293, 45.11908571327821, 5, 2.9500802850138435),
                         (3.558881521157093, 43.30564464977889, 5, 2.9500802850138443),
                         (3.2072759695048925, 41.492203586279565, 5, 2.9500802850138443),
                         (2.855670417852693, 39.67876252278024, 5, 2.9500802850138435),
                         (2.5040648662004923, 37.86532145928092, 5, 2.9500802850138443),
                         (2.152459314548292, 36.051880395781595, 5, 2.9500802850138443),
                         (1.8008537628960923, 34.23843933228227, 5, 3.141592653589793),
                         (1.8008537628960923, 32.424997865608354, 5, 3.141592653589793),
                         (1.8008537628960923, 30.611556398934436, 5, 3.141592653589793),
                         (1.8008537628960923, 28.79811493226052, 5, 3.141592653589793),
                         (1.8008537628960923, 26.984673465586607, 5, 3.141592653589793),
                         (1.8008537628960923, 25.17123199891269, 5, 3.141592653589793),
                         (1.8008537628960923, 23.357790532238774, 5, 3.141592653589793),
                         (1.8008537628960923, 21.54434906556486, 5, 3.3331046482646567),
                         (2.1524593145482926, 19.73090437349411, 5, 3.3331046482646567),
                         (2.5040648662004927, 17.917459681423363, 5, 3.3331046482646567),
                         (2.855670417852693, 16.104014989352613, 5, 3.3331046482646567),
                         (3.207275969504893, 14.290570297281867, 5, 3.3331046482646567),
                         (3.558881521157093, 12.477125605211118, 5, 3.3331046482646567),
                         (3.9104870728092935, 10.66368091314037, 5, 3.3331046482646567),
                         (4.262092624461493, 8.850236221069622, 5, 3.801249585641959),
                         (5.246588270687653, 7.580828887731206, 5, 3.8012495856419597),
                         (6.231083916913813, 6.311421554392791, 5, 3.8012495856419592),
                         (7.215579563139973, 5.042014221054377, 5, 3.8012495856419592),
                         (8.200075209366133, 3.772606887715961, 5, 3.801249585641959),
                         (9.184570855592293, 2.503199554377545, 5, 4.71238898038469),
                         (11.030500051155233, 2.503199554377545, 5, 4.71238898038469),
                         (12.876429246718171, 2.503199554377545, 5, 4.71238898038469),
                         (14.722358442281111, 2.503199554377545, 5, 4.71238898038469),
                         (16.56828763784405, 2.503199554377545, 5, 5.756356396852399),
                         (17.491252447292187, 4.089962601606118, 5, 5.756356396852399),
                         (18.414217256740322, 5.67672564883469, 5, 5.756356396852397),
                         (19.33718206618846, 7.263488696063263, 5, 5.756356396852399),
                         (20.260146875636597, 8.850251743291835, 5, 5.756356396852399),
                         (21.183111685084732, 10.437014790520408, 5, 5.756356396852397),
                         (22.10607649453287, 12.02377783774898, 5, 5.756356396852399),
                         (23.029041303981007, 13.610540884977553, 5, 5.756356396852399),
                         (23.952006113429142, 15.197303932206125, 5, 6.03020588080511),
                         (24.444253795431113, 17.10141747221374, 5, 6.030205880805112),
                         (24.93650147743308, 19.005531012221354, 5, 6.03020588080511),
                         (25.42874915943505, 20.90964455222897, 5, 6.030205880805112),
                         (25.920996841437017, 22.813758092236583, 5, 6.03020588080511),
                         (26.413244523438987, 24.717871632244197, 5, 6.03020588080511),
                         (26.905492205440957, 26.62198517225181, 5, 6.030205880805112),
                         (27.397739887442924, 28.526098712259426, 5, 6.03020588080511),
                         (27.889987569444894, 30.43021225226704, 5, 6.030205880805112),
                         (28.38223525144686, 32.334325792274655, 5, 6.03020588080511),
                         (28.87448293344883, 34.23843933228227, 5, 6.03020588080511)]

        self.assert_equal_paths(tool_path, expected_path)

    def test_path_discretization_for_empty_paths(self): #pylint: disable=invalid-name
        """ Tests that the discretization function returns an empty path if an empty path is passed
        """

        discretized_path = discretize_path([], 10)

        self.assertEqual(discretized_path, [])

    def test_path_discretization_for_single_point_paths(self): #pylint: disable=invalid-name
        """ Tests that the discretization function returns a path with one point when needed
        """

        discretized_path = discretize_path([(10, 13)], 10)

        self.assertEqual(discretized_path, [(10, 13)])

    def test_path_discretization_returns_path_for_inf_step(self): #pylint: disable=invalid-name
        """ Tests that the discretization function does nothing if the step is infinite
        """

        path = [(10, 5), (15, 5)]
        discretized_path = discretize_path(path, float('inf'))

        self.assertEqual(discretized_path, path)

    def test_path_discretization_for_horizontal_segment(self): #pylint: disable=invalid-name
        """ Tests that the discretization function works for horizontal segments
        """

        path = [(10, 5), (15, 5)]
        discretized_path = discretize_path(path, 1.5)

        expected_path = [(10, 5),
                         (11.25, 5),
                         (12.5, 5),
                         (13.75, 5),
                         (15, 5)]

        self.assert_equal_paths(discretized_path, expected_path)

    def test_non_uniform_discretization(self):
        """ Tests that the discretization functon works with generic paths
        """

        path = [(0, 0), (5, 5), (6, 5), (11, 5)]
        discretized_path = discretize_path(path, 2)

        expected_path = [
            (0, 0),
            (1.25, 1.25),
            (2.5, 2.5),
            (3.75, 3.75),
            (5, 5),
            (6, 5),
            (7.66666666666666, 5),
            (9.33333333333333, 5),
            (11, 5)]

        self.assert_equal_paths(discretized_path, expected_path)


class CuttingToolPathsGeneratorTest(unittest.TestCase): # pylint: disable=too-many-public-methods
    """ Tests for the class generating tool paths for the cutting machine
    """

    def test_empty_path(self):
        """ Tests that the class returns None in case of empty input paths
        """

        generator = CuttingToolPathsGenerator([], 2)
        generator.generate()

        self.assertEqual(generator.path(), None)

    def test_throw_exception_if_path_not_closed(self): #pylint: disable=invalid-name
        """ Tests that an exception is thrown if the path is open
        """

        path = [(1, 1), (2, 2)]

        with self.assertRaises(InvalidCuttingPath) as context_manager:
            CuttingToolPathsGenerator(path, 0.1)

        exception = context_manager.exception
        self.assertEqual(exception.reason, "path is not closed")

    def test_output_path_equal_to_input_path_if_first_point_closest_to_origin(self): #pylint: disable=invalid-name
        """ Tests that output and input paths are equal when the first point is closest to origin
        """

        path = [(1, 1), (3, 4), (5, 9), (5, 7), (8, 2), (1, 1.1)]

        generator = CuttingToolPathsGenerator(path, 1)
        generator.generate()

        self.assertEqual(generator.path(), [(0, 0)] + path + [(0, 0)])

    def test_output_path_equal_to_input_path_if_last_point_closest_to_origin(self): #pylint: disable=invalid-name
        """ Tests that output and input paths are equal when the last point is closest to origin
        """

        path = [(1, 1.1), (3, 4), (5, 9), (5, 7), (8, 2), (1, 1)]

        generator = CuttingToolPathsGenerator(path, 1)
        generator.generate()

        self.assertEqual(generator.path(), [(0, 0)] + path + [(0, 0)])

    def test_output_path_starts_from_left_bottom_point(self): #pylint: disable=invalid-name
        """ Tests that the returned path starts from the point nearest to the origin

        Also tests that the returned path has the same initial and final point and that the original
        initial and final point are not duplicated in the output
        """

        path = [(5, 7), (3, 4), (5, 9), (1, 1), (8, 2), (5, 7)]

        generator = CuttingToolPathsGenerator(path, 1)
        generator.generate()

        # Same initial and final point (the one closest to (0, 0) and (5, 7) not repeated
        expected_path = [(0, 0), (1, 1), (8, 2), (5, 7), (3, 4), (5, 9), (1, 1), (0, 0)]

        self.assertEqual(generator.path(), expected_path)

    def test_border_with_no_margin(self):
        """ Tests that commands to square the piece are added if requested

        Margin is 0, path starts from the point nearest to (0, 0)
        """

        border = Border([[(0, 0), (10, 20)]], 0)
        path = [(5, 7), (3, 4), (5, 9), (1, 1), (8, 2), (5, 7)]

        generator = CuttingToolPathsGenerator(path, 1, border)
        generator.generate()

        # Same initial and final point (the one closest to (0, 0) and (5, 7) not repeated
        expected_path = [(0, 0), (1, 1), (8, 2), (5, 7), (3, 4), (5, 9), (1, 1), (0, 0), (10, 0),
                         (10, 20), (0, 20), (0, 0)]

        self.assertEqual(generator.path(), expected_path)

    def test_border_with_margin(self):
        """ Tests that commands to square the piece with a margin are added if requested

        Path starts with the point nearest to the bottom left border point
        """

        border = Border([[(2, 2), (8, 18)]], 0)
        path = [(5, 7), (3, 4), (5, 9), (1, 1), (2.1, 2.1), (8, 2), (5, 7)]

        generator = CuttingToolPathsGenerator(path, 1, border)
        generator.generate()

        # Same initial and final point (the one closest to (0, 0) and (5, 7) not repeated
        expected_path = [(0, 0), (2, 2), (2.1, 2.1), (8, 2), (5, 7), (3, 4), (5, 9), (1, 1),
                         (2.1, 2.1), (2, 2), (8, 2), (8, 18), (2, 18), (2, 2), (0, 0)]

        self.assertEqual(generator.path(), expected_path)
