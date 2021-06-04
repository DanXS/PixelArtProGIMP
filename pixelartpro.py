#!/usr/bin/env python

import json
import os
import sys
from gimpfu import *

verbose = True

# Utility code

def is_pap_bundle(dirname):
	if os.path.isdir(dirname):
		parts = os.path.splitext(dirname)
		if parts[1] == ".pap":
			return True
	return False

def add_extenstion_if_missing(dirname):
	parts = os.path.splitext(dirname)
	if len(parts[1]) == 0:
		new_dirname = dirname + ".pap"
		os.rename(dirname, new_dirname)
		return new_dirname
	return dirname

# Create new code

def create_new(image, width, height, num_frames, num_layers, bgColour, hasBackground):
	for i in range(0, num_frames):
		layer_group = pdb.gimp_layer_group_new(image)
		pdb.gimp_layer_set_name(layer_group, "Frame_" + str(i+1))
		if i == 0:
			pdb.gimp_layer_set_visible(layer_group, TRUE)
		else:
			pdb.gimp_layer_set_visible(layer_group, FALSE)
		pdb.gimp_image_insert_layer(image, layer_group, None, 0)
		if hasBackground:
			layer = pdb.gimp_layer_new(image, width, height, RGBA_IMAGE, "Background", 100, LAYER_MODE_NORMAL)
			pdb.gimp_image_insert_layer(image, layer, layer_group, 0)
			drw = pdb.gimp_image_active_drawable(image)
			pdb.gimp_context_set_background(bgColour)
			pdb.gimp_drawable_fill(drw, BACKGROUND_FILL)
		for j in range(0, num_layers):
			layer_name = "Layer_" + str(j)
			layer = pdb.gimp_layer_new(image, width, height, RGBA_IMAGE, layer_name, 100, LAYER_MODE_NORMAL)
			pdb.gimp_image_insert_layer(image, layer, layer_group, 0)

def bundle_pixelartpro_new(width_opt, height_opt, num_frames, num_layers, bgColour, hasBackground):
	sizes = [8, 16, 24, 32, 64, 96, 128, 192, 256]
	width = sizes[width_opt]
	height = sizes[height_opt]
	num_frames = int(num_frames)
	num_layers = int(num_layers)
	if verbose:
		print("Width: " + str(width))
		print("Height: " + str(height))
		print("Number of frames: " + str(num_frames))
		print("Number of layers: " + str(num_layers))
		print("Background colour: " + str(bgColour))
		print("Has background:" + str(hasBackground))
	image = pdb.gimp_image_new(width, height, RGB_IMAGE)
	create_new(image, width, height, num_frames, num_layers, bgColour, hasBackground)
	display = pdb.gimp_display_new(image)

# Tile code

def bundle_pixelartpro_tile(image, drawable):
	background = pdb.gimp_context_get_background()
	palette_name = pdb.gimp_context_get_palette()
	tile_width = drawable.width
	tile_height = drawable.height
	frame_names = get_frame_group_names(image)
	dest_width = 1024
	dest_height = ((len(frame_names) * tile_width) / dest_width)*tile_height+tile_height
	if verbose:
		print("Tile sheet size = " + str(dest_width) + ", " + str(dest_height))
	dest_image = pdb.gimp_image_new(dest_width, dest_height, RGB_IMAGE)
	for i in range(0, len(frame_names)):
		x_pos = (i * tile_width) % dest_width
		y_pos = ((i * tile_width) / dest_width)*tile_height
		if verbose:
			print("Creating tile at :" + str(x_pos) + ", " + str(y_pos) + " for " + frame_names[i])
		layer_group = pdb.gimp_layer_group_new(dest_image)
		pdb.gimp_layer_set_name(layer_group, frame_names[i])
		pdb.gimp_image_insert_layer(dest_image, layer_group, None, 0)
		layer_names = get_frame_layer_names(image, frame_names[i])
		for j in range(0, len(layer_names)):
			layer = pdb.gimp_image_get_layer_by_name(image, layer_names[j])
			new_layer = pdb.gimp_layer_new_from_drawable(layer, dest_image)
			pdb.gimp_layer_set_offsets(new_layer, x_pos, y_pos)
			pdb.gimp_item_set_name(new_layer, layer_names[j])
			pdb.gimp_image_insert_layer(dest_image, new_layer, layer_group, 0)
	display = pdb.gimp_display_new(dest_image)
	pdb.gimp_context_set_background(background)
	pdb.gimp_context_set_palette(palette_name)

# Stack code

def bundle_pixelartpro_stack(image, drawable):
	background = pdb.gimp_context_get_background()
	palette_name = pdb.gimp_context_get_palette()
	tile_width = drawable.width
	tile_height = drawable.height
	frame_names = get_frame_group_names(image)
	dest_image = pdb.gimp_image_new(tile_width, tile_height, RGB_IMAGE)
	for i in range(0, len(frame_names)):
		layer_group = pdb.gimp_layer_group_new(dest_image)
		if i == 0:
			pdb.gimp_layer_set_visible(layer_group, TRUE)
		else:
			pdb.gimp_layer_set_visible(layer_group, FALSE)
		pdb.gimp_layer_set_name(layer_group, frame_names[i])
		pdb.gimp_image_insert_layer(dest_image, layer_group, None, 0)
		layer_names = get_frame_layer_names(image, frame_names[i])
		for j in range(0, len(layer_names)):
			layer = pdb.gimp_image_get_layer_by_name(image, layer_names[j])
			new_layer = pdb.gimp_layer_new_from_drawable(layer, dest_image)
			pdb.gimp_layer_set_offsets(new_layer, 0, 0)
			pdb.gimp_item_set_name(new_layer, layer_names[j])
			pdb.gimp_image_insert_layer(dest_image, new_layer, layer_group, 0)
	display = pdb.gimp_display_new(dest_image)
	pdb.gimp_context_set_background(background)
	pdb.gimp_context_set_palette(palette_name)

# Loading code

def load_colour(colour_dict):
	if colour_dict == None:
		return None
	r = int(255.0*colour_dict.get("r"))
	g = int(255.0*colour_dict.get("g"))
	b = int(255.0*colour_dict.get("b"))
	a = int(255.0*colour_dict.get("a"))
	return (r,g,b,a)

def load_palette(palette_array):
	out = []
	if palette_array == None:
		return out
	if not (palette_array is None):
		for i in range(0, len(palette_array)):
			out.append(load_colour(palette_array[i]))
	return out

def load_frames(in_dir, image, bgColour, width, height, frames_array):
	for i in range(0, len(frames_array)):
		if verbose:
			print("frame : " + str(i+1))
		layer_group = pdb.gimp_layer_group_new(image)
		pdb.gimp_layer_set_name(layer_group, "Frame_" + str(i+1))
		if i == 0:
			pdb.gimp_layer_set_visible(layer_group, TRUE)
		else:
			pdb.gimp_layer_set_visible(layer_group, FALSE)
		pdb.gimp_image_insert_layer(image, layer_group, None, 0)
		layers_array = frames_array[i].get("layers")
		if bgColour != None:
			layer = pdb.gimp_layer_new(image, width, height, RGBA_IMAGE, "Background", 100, LAYER_MODE_NORMAL)
			pdb.gimp_image_insert_layer(image, layer, layer_group, 0)
			drw = pdb.gimp_image_active_drawable(image)
			pdb.gimp_context_set_background((bgColour[0], bgColour[1], bgColour[2], bgColour[3]))
			pdb.gimp_drawable_fill(drw, BACKGROUND_FILL)
		for j in range(0, len(layers_array)):
			layer_id = layers_array[j].get("id")
			layer_name = layers_array[j].get("name")
			layer_visible = layers_array[j].get("visible")
			layer_locked = layers_array[j].get("locked")
			if layer_name is None:
				layer_name = "Layer_" + str(layer_id)
			if verbose:
				print("layer id : " + str(layer_id))
				print("layer name : " + layer_name)
				print("layer visible : " + str(layer_visible))
				print("layer locked : " + str(layer_locked))
			filename = "Frame_" + str(i) + "_Layer_" + str(j) + ".png"
			if verbose:
				print("loading : " + filename)
			path = os.path.join(in_dir, filename)
			layer = pdb.gimp_file_load_layer(image, path)
			pdb.gimp_layer_set_name(layer, layer_name)
			pdb.gimp_image_insert_layer(image, layer, layer_group, 0)


def bundle_pixelartpro_load(dirname):
	if dirname == None:
		pdb.gimp_message("No pap bundle provided!")
		return
	parts = os.path.splitext(dirname)
	if parts[1] != ".pap":
		pdb.gimp_message("Not a PixelArtPro (.pap) bundle")
		return
	path = os.path.join(dirname, "info.json")
	with open(path) as f:
		info_dict = json.load(f)
		width = info_dict.get("width")
		height = info_dict.get("height")
		fps = info_dict.get("fps")
		bgColour = load_colour(info_dict.get("bgColour"))
		palette = load_palette(info_dict.get("palette"))
		if verbose:
			print("width : " + str(width))
			print("height : " + str(height))
			print("fps : " + str(fps))
			print("bgColour : " + str(bgColour))
			print("palette : " + str(palette))
		image = pdb.gimp_image_new(width, height, RGB_IMAGE)
		if len(palette) > 0:
			name = os.path.splitext(os.path.basename(dirname))[0]
			palette_name = name + "_palette"
			actual_name = pdb.gimp_palette_new(palette_name)
			for i in range(0, len(palette)):
				pdb.gimp_palette_add_entry(actual_name, palette_name+str(i), (palette[i][0], palette[i][1], palette[i][2], palette[i][3]))
			pdb.gimp_context_set_palette(actual_name)
		load_frames(dirname, image, bgColour, width, height, info_dict.get("frames"))
		display = pdb.gimp_display_new(image)

# Saving code

def get_colour_dict(colour):
	return {"r" : colour.r, "g" : colour.g, "b" : colour.b, "a" : colour.a}

def get_pallete_entries(palette_name):
	out = []
	num_colours, colours = pdb.gimp_palette_get_colors(palette_name)
	for i in range(0, num_colours):
		colour_dict = get_colour_dict(colours[i])
		out.append(colour_dict)
	return out

def filter_layer_names_for_save(layer_names):
	out = []
	for layer_name in layer_names:
		if "Background" not in layer_name:
			index = layer_name.find("#")
			if index != -1:
				layer_name = layer_name[:index-1]
			out.append(layer_name)
	return out


def get_frame_layer_names(image, frame_name):
	layer = pdb.gimp_image_get_layer_by_name(image, frame_name)
	layer_names = []
	for layer in layer.layers:
		if pdb.gimp_item_is_layer(layer):
			name = pdb.gimp_item_get_name(layer)
			layer_names.insert(0, name)
	return layer_names


def get_frame_group_names(image):
	group_names = []
	for layer in image.layers:
		if pdb.gimp_item_is_group(layer):
			name = pdb.gimp_item_get_name(layer)
			group_names.insert(0, name)
	return group_names

def save_info(image, drawable, dirname):
	background = pdb.gimp_context_get_background()
	bgColour = get_colour_dict(background)
	palette_name = pdb.gimp_context_get_palette()
	palette = get_pallete_entries(palette_name)
	group_names = get_frame_group_names(image)
	frames = []
	for group_name in group_names:
		layer_names = filter_layer_names_for_save(get_frame_layer_names(image, group_name))
		layers = []
		for i in range(0, len(layer_names)):
			layer_dict = {
			"id" : i,
			"name" : layer_names[i],
			"locked" : False,
			"visible" : True
			}
			layers.append(layer_dict)
		frames.append({"layers" : layers})
	info = {
	"width" : drawable.width,
	"height" : drawable.height,
	"fps" : 6,
	"bgColour" : bgColour,
	"palette" : palette,
	"frames" : frames
	}
	path = os.path.join(dirname, "info.json")
	with open(path, 'w') as outfile:
		json.dump(info, outfile, indent=4)

def save_layer_images(image, dirname):
	frame_names = get_frame_group_names(image)
	for i in range(0, len(frame_names)):
		raw_filename = "Frame_" + str(i) + ".png"
		layer = pdb.gimp_image_get_layer_by_name(image, frame_names[i])
		filename = os.path.join(dirname, raw_filename)
		pdb.gimp_file_save(image, layer, filename, raw_filename)
		layer_names = get_frame_layer_names(image, frame_names[i])
		layer_names = list(filter(lambda x: ("Background" not in x), layer_names))
		for j in range(0, len(layer_names)):
			raw_filename = "Frame_" + str(i) + "_Layer_" + str(j) + ".png"
			layer = pdb.gimp_image_get_layer_by_name(image, layer_names[j])
			filename = os.path.join(dirname, raw_filename)
			pdb.gimp_file_save(image, layer, filename, raw_filename)


def bundle_pixelartpro_save(image, drawable, dirname):
	if image is None or drawable is None:
		pdb.gimp_message("No active project to save")
		return
	if dirname is None or not os.path.isdir(dirname):
		pdb.gimp_message("Directory does not exist - not saved")
		return
	if len(os.listdir(dirname)) != 0:
		pdb.gimp_message("Directory not empty, please create an empty directory to save to!")
		return
	dirname = add_extenstion_if_missing(dirname)
	save_info(image, drawable, dirname)
	save_layer_images(image, dirname)


register(
	"bundle-pixelartpro-new",                           
	"Create a new PixelArtPro project",
	"Create a new empty pixel art project with initial frames and layers",
	"Dan Shepherd",
	"Dan Shepherd",
	"Feb 2021",
	"New...",
	None, 
	[
		(PF_OPTION, 'width_opt',   'Width:', 0, ['8', '16', '24', '32', '64', '96', '128', '192', '256']),
		(PF_OPTION, 'height_opt',   'Height:', 0, ['8', '16', '24', '32', '64', '96', '128', '192', '256']),
		(PF_SPINNER, 'num_frames', 'Frames:', 1, (1, 200, 1)),
		(PF_SPINNER, 'num_layers', 'Layers:', 1, (1, 50, 1)),
		(PF_COLOR, "bgColour", "Background Colour:", (255, 255, 255)),
		(PF_TOGGLE, "useBackground",   "Has Background?", 1)
	],
	[],
	bundle_pixelartpro_new,
	menu = "<Image>/Filters/Languages/Python-Fu/PixelArtPro"
	)

register("bundle-pixelartpro-tile",                           
	"Tile layout for PixelArtPro project",
	"Convert to tile layout for pixel art project",
	"Dan Shepherd",
	"Dan Shepherd",
	"Feb 2021",
	"Tile",
	"RGBA", 
	[
		(PF_IMAGE, "image", "Input image", None),
		(PF_DRAWABLE, "drawable", "Input drawable", None)
	],
	[],
	bundle_pixelartpro_tile,
	menu = "<Image>/Filters/Languages/Python-Fu/PixelArtPro"
	)

register("bundle-pixelartpro-stack",                           
	"Stack layout for PixelArtPro project",
	"Convert to stack layout for pixel art project",
	"Dan Shepherd",
	"Dan Shepherd",
	"Feb 2021",
	"Stack",
	"RGBA", 
	[
		(PF_IMAGE, "image", "Input image", None),
		(PF_DRAWABLE, "drawable", "Input drawable", None)
	],
	[],
	bundle_pixelartpro_stack,
	menu = "<Image>/Filters/Languages/Python-Fu/PixelArtPro"
	)

register(
	"bundle-pixelartpro-load",                           
	"Load PixelArtPro (.pap) bundle",
	"Load a PixelArtPro bundle which include frames and layers and a potentially a palette.",
	"Dan Shepherd",
	"Dan Shepherd",
	"Feb 2021",
	"Open...",
	None, 
	[
        (PF_DIRNAME, 'directory', 'The name of the pap directory to load', None),
	],
	[],
	bundle_pixelartpro_load,
	menu = "<Image>/Filters/Languages/Python-Fu/PixelArtPro"
	)

register(
	"bundle-pixelartpro-save",                           
	"Save PixelArtPro (.pap) bundle",
	"Save a PixelArtPro bundle which include frames and layers and a potentially a palette.",
	"Dan Shepherd",
	"Dan Shepherd",
	"Feb 2021",
	"Save...",
	"RGBA", 
	[
		(PF_IMAGE, "image", "Input image", None),
		(PF_DRAWABLE, "drawable", "Input drawable", None),
		(PF_DIRNAME, 'directory', 'The name of the pap directory to save', None)
	],
	[],
	bundle_pixelartpro_save,
	menu = "<Image>/Filters/Languages/Python-Fu/PixelArtPro"
	)

main()

