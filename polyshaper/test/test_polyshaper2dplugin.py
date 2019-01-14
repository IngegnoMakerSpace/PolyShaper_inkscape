#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper plugin tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from polyshaper2dplugin import Polyshaper2D # pylint: disable=no-name-in-module

class Polyshaper2DTest(unittest.TestCase):
    """ Tests for the main class of the Polyshaper inkscape plugin
    """

    def test_short_form_commandline(self):
        """ Tests that all expected short commandline parameters are accepted
        """
        polyshaper = Polyshaper2D()

        options = polyshaper.OptionParser.parse_args([
            "execName",
            "-n", "pippo",
            "-x", "13",
            "-y", "17",
            "-s", "42",
            "-b", "7",
            "-c", "True",
            "-m", "4",
            "-t", "pippo",
            "-p", "True",
            "-a", "True"
            ])[0]

        self.assertEqual(options.shapename, "pippo")
        self.assertEqual(options.dim_x, 13)
        self.assertEqual(options.dim_y, 17)
        self.assertEqual(options.speed, 42)
        self.assertEqual(options.flatness, 7)
        self.assertEqual(options.square, True)
        self.assertEqual(options.margin, 4)
        self.assertEqual(options.machine_type, "pippo")
        self.assertEqual(options.draw_toolpath, True)
        self.assertEqual(options.auto_close_path, True)

    def test_long_form_commandline(self):
        """ Tests that all expected long commandline parameters are accepted
        """
        polyshaper = Polyshaper2D()

        options = polyshaper.OptionParser.parse_args([
            "execName",
            "--shapename", "pippo",
            "--dim-x", "13",
            "--dim-y", "17",
            "--speed", "42",
            "--flatness", "7",
            "--square", "True",
            "--margin", "4",
            "--type", "pippo",
            "--draw-toolpath", "True",
            "--auto-close-path", "True",
            "--active-tab", "pluto"
            ])[0]

        self.assertEqual(options.shapename, "pippo")
        self.assertEqual(options.dim_x, 13)
        self.assertEqual(options.dim_y, 17)
        self.assertEqual(options.speed, 42)
        self.assertEqual(options.flatness, 7)
        self.assertEqual(options.square, True)
        self.assertEqual(options.margin, 4)
        self.assertEqual(options.machine_type, "pippo")
        self.assertEqual(options.draw_toolpath, True)
        self.assertEqual(options.auto_close_path, True)
        self.assertEqual(options.active_tab, "pluto")
