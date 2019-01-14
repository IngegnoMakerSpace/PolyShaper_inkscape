#!/usr/bin/env python2
# -*- encoding:utf-8 -*-

"""
The script to start all tests in the directory

To add new tests remember to:
    1) import the test
    2) add the test suite to the list
(modify the portion of code between the lines of # characters)
"""

import unittest
import sys

# The directory with inkscape extensions (needed to import modules required by
# the plugin)
INKSCAPE_EXTENSION_DIRECTORY = "/usr/share/inkscape/extensions"

# Adding directories with plugins and the gloal inkscape extensions directory
sys.path.insert(1, sys.path[0] + "/../plugin")
sys.path.insert(2, INKSCAPE_EXTENSION_DIRECTORY)

################################################################################
### Import new tests here...
from test_polyshaperengravingplugin import PolyshaperEngravingTest  # pylint: disable=wrong-import-position
from test_polyshaper2dplugin import Polyshaper2DTest # pylint: disable=wrong-import-position
from test_polyshaper.test_workingarea import WorkingAreaGeneratorTest # pylint: disable=wrong-import-position
from test_polyshaper.test_pathsextraction import FlattenBezierTest # pylint: disable=wrong-import-position
from test_polyshaper.test_pathsextraction import PathsExtractorTest # pylint: disable=wrong-import-position
from test_polyshaper.test_pathsunion import PathsJoinerTest # pylint: disable=wrong-import-position
from test_polyshaper.test_toolpaths import EngravingToolPathsGeneratorTest # pylint: disable=wrong-import-position
from test_polyshaper.test_toolpaths import CuttingToolPathsGeneratorTest # pylint: disable=wrong-import-position
from test_polyshaper.test_gcode import EngravingGCodeGeneratorTest # pylint: disable=wrong-import-position
from test_polyshaper.test_gcode import CuttingGCodeGeneratorTest # pylint: disable=wrong-import-position
from test_polyshaper.test_helpers import HelpersTest # pylint: disable=wrong-import-position
from test_polyshaper.test_machine import MachineTest # pylint: disable=wrong-import-position
from test_polyshaper.test_pathinfo import PathInfoTest # pylint: disable=wrong-import-position
from test_polyshaper.test_toolpathpainter import ToolPathPainterTest # pylint: disable=wrong-import-position
from test_polyshaper.test_border import BorderTest # pylint: disable=wrong-import-position
from test_polyshaper.test_border import BorderPainterTest # pylint: disable=wrong-import-position

### ... and add test suites here
TEST_SUITES = [
    PolyshaperEngravingTest,
    Polyshaper2DTest,
    WorkingAreaGeneratorTest,
    FlattenBezierTest,
    PathsExtractorTest,
    PathsJoinerTest,
    EngravingToolPathsGeneratorTest,
    CuttingToolPathsGeneratorTest,
    EngravingGCodeGeneratorTest,
    CuttingGCodeGeneratorTest,
    HelpersTest,
    MachineTest,
    PathInfoTest,
    ToolPathPainterTest,
    BorderTest,
    BorderPainterTest
]
################################################################################

if __name__ == '__main__':
    all_suites = [] # pylint: disable=invalid-name
    for s in TEST_SUITES:
        all_suites.append(unittest.TestLoader().loadTestsFromTestCase(s))

    unittest.TextTestRunner(verbosity=3).run(unittest.TestSuite(all_suites))

### TODO See this list of todos
# 2) Vedere se si può disabilitare "Anteprima diretta" (o togliendo checkbox o controllando da
#    codice se è abilitata e mettendo solo area o qualcosa del genere)
# 3) Provare a togliere tutte le eccezioni di pylint dal codice (i disable=...)
# 4) Ricontrollare tutto il codice: è PolyShaper e non Polyshaper!!!
# 5) Ricontrollare uso di _(): serve importare gettext? o forse inkex?
# 6) METTERE UN FILE DI CONFIGURAZIONE PER PYLINT E DIRE CHE FUNZIONI CHE INIZIANO CON test_ POSSONO
#    ANCHE ESSERE MOLTO LUNGHE
# 7) VEDERE SE È POSSIBILE DIRE A PYLINT DOVE PRENDERE GLI IMPORT (FORSE SI PUÒ ESPORTARE
#    PYTHONPATH, VEDERE I VALORI CHE SONO MESSI IN testall.py)
# 8) METTERE TRAVIS (PER CI https://travis-ci.org/) SU GITHUB, DIRE A FLAVIO DI FARLO (IO NON HO
#    PERMESSI SUFFICIENTI SUL REPOSITORY)
# 9) METTERE COVERALLS (PER COVERAGE https://coveralls.io/) SU GITHUB
# 10) Find a cross platform way to identify the path of the desktop directory and save files there
