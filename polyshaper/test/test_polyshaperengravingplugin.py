#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper plugin tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

# NOTE: Find a way to tell pylint that function names in tests can be arbitrarily long

import unittest
from polyshaperengravingplugin import PolyshaperEngraving # pylint: disable=no-name-in-module

class PolyshaperEngravingTest(unittest.TestCase):
    """ Tests for the main class of the PolyshaperEngraving inkscape plugin
    """

    def test_short_form_commandline(self):
        """ Tests that all expected short commandline parameters are accepted
        """
        polyshaper = PolyshaperEngraving()

        options = polyshaper.OptionParser.parse_args([
            "execName",
            "-f", "pippo",
            "-x", "13",
            "-y", "17",
            "-z", "42"
            ])[0]

        self.assertEqual(options.filename, "pippo")
        self.assertEqual(options.dim_x, 13)
        self.assertEqual(options.dim_y, 17)
        self.assertEqual(options.depth_z, 42)

    def test_long_form_commandline(self):
        """ Tests that all expected long commandline parameters are accepted
        """
        polyshaper = PolyshaperEngraving()

        options = polyshaper.OptionParser.parse_args([
            "execName",
            "--filename", "pippo",
            "--dim-x", "13",
            "--dim-y", "17",
            "--depth-z", "42",
            "--active-tab", "pluto"
            ])[0]

        self.assertEqual(options.filename, "pippo")
        self.assertEqual(options.dim_x, 13)
        self.assertEqual(options.dim_y, 17)
        self.assertEqual(options.depth_z, 42)
        self.assertEqual(options.active_tab, "pluto")
