#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
Polyshaper machines definition tests

NOTE: to run this test standalone you must add ../plugin to the PYTHONPATH shell
variable tro to sys.path as well as the global inkscape plugin directory. If run
through testAll.py, there is no need to add directories (they are inserted by
that script)
"""

import unittest
from polyshaper.machine import Machine, machine_factory # pylint: disable=import-error,no-name-in-module

class MachineTest(unittest.TestCase):
    """ Tests the machines definition
    """

    def test_return_None_for_invalid_names(self): #pylint: disable=invalid-name
        """ Tests that the factory returns None for invalid names
        """

        self.assertIsNone(machine_factory("bla bla bla"))

    def test_abstract_class(self):
        """ Tests that all methods of Machine are abstract
        """

        self.assertRaises(NotImplementedError, Machine)

    def test_piece_dimensions_allowed(self):
        """ Tests that the piece_dimensions_allowed works
        """

        class TestMachine(Machine): #pylint: disable=missing-docstring
            def __init__(self):
                pass
            def working_area_width(self): #pylint: disable=missing-docstring,no-self-use
                return 100
            def working_area_height(self): #pylint: disable=missing-docstring,no-self-use
                return 200

        machine = TestMachine()

        self.assertTrue(machine.piece_dimensions_allowed(100, 200))
        self.assertFalse(machine.piece_dimensions_allowed(101, 50))
        self.assertFalse(machine.piece_dimensions_allowed(50, 201))

    def test_P400(self): #pylint: disable=invalid-name
        """ Tests definition for the P400
        """

        machine = machine_factory("P400")

        self.assertEqual(machine.name(), "P400")
        self.assertEqual(machine.working_area_width(), 400)
        self.assertEqual(machine.working_area_height(), 400)

    def test_PolyShaperAzul(self): #pylint: disable=invalid-name
        """ Tests definition for the P1000
        """

        machine = machine_factory("PolyShaperAzul")

        self.assertEqual(machine.name(), "PolyShaper Azul")
        self.assertEqual(machine.working_area_width(), 1000)
        self.assertEqual(machine.working_area_height(), 500)

    def test_PolyShaperAzulPlus(self): #pylint: disable=invalid-name
        """ Tests definition for the P1000plus
        """

        machine = machine_factory("PolyShaperAzul+")

        self.assertEqual(machine.name(), "PolyShaper Azul+")
        self.assertEqual(machine.working_area_width(), 1200)
        self.assertEqual(machine.working_area_height(), 600)

    def test_PolyShaperGraent(self): #pylint: disable=invalid-name
        """ Tests definition for the P1100
        """

        machine = machine_factory("PolyShaperGrænt")

        self.assertEqual(machine.name(), "PolyShaper Grænt")
        self.assertEqual(machine.working_area_width(), 1100)
        self.assertEqual(machine.working_area_height(), 1100)

    def test_PolyShaperOranje(self): #pylint: disable=invalid-name
        """ Tests definition for the Oranje
        """

        machine = machine_factory("PolyShaperOranje")

        self.assertEqual(machine.name(), "PolyShaper Oranje")
        self.assertEqual(machine.working_area_width(), 500)
        self.assertEqual(machine.working_area_height(), 500)
