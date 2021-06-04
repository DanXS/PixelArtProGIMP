# PixelArtProGIMP
GIMP plugin for Pixel Art Pro (pap) files.

This folder contains a plugin for GIMP-2.10 which will allow Pixel Art Pro (.pap) files to be load/save or created within gimp.  Frames are stacked as layer groups with each layer inside the group representing the layers in the Pixel Art Pro iPhone/iPad application.  Note this is for Pixel Art Pro version 2.0. Prior to that Pixel Art Pro did not support export to .pap files.

Essentailly a .pap file isn't a file at all it's a bundle or directory containing all the .png files for each layer of each frame and an info.json file which has additional information about the size of the item and the number of layers, layer names etc, basically everything Pixel Art Pro needs to know about the item.

Instructions:

Copy pixelartpro.py to GIMP's plugin directory, on mac this is:
~/Library/Application Support/GIMP/2.10/plug-ins

Inside gimp the plug-is all appear under the menu, Filters->Python-Fu->PixelArtPro. Note that I didn't use the normal import/export locations because the behaviour of the gimp loader expects a file and not a directory where as .pap files are actually directories which confuses the loader.

Functions supported by the plug-in

New - create a new file within gimp specifiy frames and layers
Open - open a .pap file
Save - save a .pap file
Stack - stack frames one on top of each other
Tile - layout frames suitable for a file map


