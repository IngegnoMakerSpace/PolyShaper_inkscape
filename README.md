# PolyShaper_inkscape

An Inkscape plugin for the Polyshaper CNC.

To use the plugin, copy the files

- polyshaper/plugin/polyshaper2dplugin.inx
- polyshaper/plugin/polyshaper2dplugin.py
- polyshaper/plugin/polyshaperengravingplugin.inx
- polyshaper/plugin/polyshaperengravingplugin.py

and the directory

- polyshaper/plugin/polyshaper

into the inkscape user plugin directory (to find out which directory inkscape uses for plugins, go to
**Edit->Preferences->System** and check the value of *User extensions*)

To launch tests and pylint on plugin code, run the verify.sh bash script
