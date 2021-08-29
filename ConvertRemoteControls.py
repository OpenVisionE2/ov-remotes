#!/usr/bin/python
#
# 	ConvertRemoteControl.py
#
# 	Copyright (c) 2021  IanSav.  All rights reserved.
#
# 	GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
#
# 	This program is free software: you can redistribute it and/or
# 	modify it under the terms of the GNU General Public License as
# 	published by the Free Software Foundation.  It is open source,
# 	you are allowed to use and modify it so long as you attribute
# 	and acknowledge the source and original author.  That is, the
# 	license, original author and this message must be retained at
# 	all times.
#
# 	This code was developed as open source software it should not
# 	be commercially distributed or included in any commercial
# 	software or used for commercial benefit.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	See <https://www.gnu.org/licenses/>.

from errno import ENOENT
from os import listdir
from os.path import isfile, join as pathjoin
from sys import argv
from xml.etree.cElementTree import ParseError, parse, fromstring

from KeyBindings import keyDescriptions
from keyids import KEYIDS, KEYIDNAMES

VERSION = "1.1  -  26-May-2021"

LOG_SILENT = 0
LOG_PROGRAM = 1
LOG_REPORT = 2
LOG_ERROR = 3
LOG_ALERT = 4
LOG_WARNING = 5
LOG_NOTE = 6
LOG_INFORMATION = 7
LOG_DEBUG = 8
LOG_LEVELS = {
	LOG_SILENT: "Silent",
	LOG_PROGRAM: "Program",
	LOG_REPORT: "Report",
	LOG_ERROR: "Error",
	LOG_ALERT: "Alert",
	LOG_WARNING: "Warning",
	LOG_NOTE: "Note",
	LOG_INFORMATION: "Information",
	LOG_DEBUG: "Debug"
}

SORT_SEQUENCE = 0
SORT_POSITION = 1
SORT_KEYID = 2
SORT_LABEL = 3
SORT_ORDERS = [
	"file entry",
	"button position",
	"keyid",
	"label"
]

FORMAT_UNCHANGED = 0
FORMAT_CAPITALISE = 1
FORMAT_UPPERCASE = 2
FORMATS = [
	"unchanged",
	"capitalised",
	"uppercased"
]

ALLIANCE_IMAGE_PATH = "/static/remotes/"
REMOTE_IMAGE_PATH = "/images/remotes/"

LOG_LEVEL = LOG_INFORMATION
SORT_ORDER = SORT_POSITION
FORMAT_LABELS = FORMAT_CAPITALISE
FORMAT_TITLES = FORMAT_CAPITALISE
USE_ALLIANCE_PATH = False

AUTO_CORRECT = {
	"CH-": "BOUQUET-",
	"CH+": "BOUQUET+",
	"CHANNEL-": "BOUQUET-",
	"CHANNEL+": "BOUQUET+",
	"CONTEXT_MENU": "CONTEXT",
	"DREAMSELECT": "UNKNOWN",
	"FAVORITES": "FAV",
	"FFW": "FASTFORWARD",
	"FILELIST": "LIST",
	"FORWARD": "FASTFORWARD",
	"MODE": "VMODE",
	"NEXT": "ARROWRIGHT",
	"PORTAL": "PLUGIN",
	"PORV": "FAV",
	"PREVIOUS": "ARROWLEFT",
	"PROGRAMM": "TIMER",
	"RES": "VMODE",
	"REW": "REWIND",
	"RRW": "REWIND",
	"SHIFT": "UNKNOWN",
	"SKIPBACK": "PREVIOUSSONG",
	"SKIPFORWARD": "NEXTSONG",
	"SWITCHVIDEOMODE": "VMODE",
	"TIME": "TIMER",
	"TOUCHPAD_TOGGLE": "UNKNOWN",
	"TV-OUT": "VMODE",
	"TVSELECT": "UNKNOWN",
	"WEB": "WWW"
}


# Load the XML specifications for the remote control.
#
def loadRemoteXML(filename):
	logMessage(LOG_REPORT, "Loading remote control XML definition file '%s'." % filename)
	domXML = None
	try:
		with open(filename, "r") as fd:  # This open gets around a possible file handle leak in Python's XML parser.
			try:
				domXML = parse(fd).getroot()
			except ParseError as err:
				fd.seek(0)
				content = fd.readlines()
				line, column = err.position
				print("  XML Parse Error: '%s' in '%s'!" % (err, filename))
				data = content[line - 1].replace("\t", " ").rstrip()
				print("  XML Parse Error: '%s'" % data)
				print("  XML Parse Error: '%s^%s'" % ("-" * column, " " * (len(data) - column - 1)))
			except Exception as err:
				print("  Error: Unable to parse XML remote control data in '%s' - '%s'!" % (filename, err))
	except (IOError, OSError) as err:
		if err.errno == ENOENT:  # No such file or directory
			print("  Warning: Remote control XML file '%s' does not exist!" % filename)
		else:
			print("  Error %d: Opening remote control XML file '%s'! (%s)" % (err.errno, filename, err.strerror))
	except Exception as err:
		print("  Error: Unexpected error opening remote control XML file '%s'! (%s)" % (filename, err))
	if domXML is None:
		return None
	rc = domXML.find("rc")
	if rc is None:
		logMessage(LOG_ERROR, "Remote control XML file structure is invalid!")
		return None
	rcButtons = {}
	bindIndex = rc.attrib.get("id")
	if bindIndex:
		msg = " but being processed as '%d'"
		# if filename == "dmm0":
		# 	index = 0
		# elif filename.startswith("dmm"):
		# 	index = 1
		if filename == "xp1000":
			index = 3
		elif filename == "formuler1":
			index = 4
		else:
			index = 2
		msg = msg % index
		if bindIndex == str(index):
			msg = ""
		logMessage(LOG_REPORT, "Remote control id defined as '%s'%s." % (bindIndex, msg))
		rcButtons["id"] = index
	else:
		logMessage(LOG_REPORT, "Remote control id is undefined so '2' will be assumed.")
		rcButtons["id"] = 2
	image = rc.attrib.get("image")
	if image:
		if not USE_ALLIANCE_PATH and image.startswith(ALLIANCE_IMAGE_PATH):
			image = pathjoin(REMOTE_IMAGE_PATH, "%s.png" % image.split("/")[3])
		rcButtons["image"] = image
	rcButtons["buttons"] = []
	sequence = 0
	for button in rc.findall("button"):
		sequence += 1
		id = button.attrib.get("id")
		remap = button.attrib.get("remap")
		name = button.attrib.get("name")
		label = formatLine(button.attrib.get("label"), FORMAT_LABELS)
		pos = button.attrib.get("pos")
		title = formatLine(button.attrib.get("title"), FORMAT_TITLES)
		shape = button.attrib.get("shape")
		coords = button.attrib.get("coords")
		radius = button.attrib.get("radius")
		size = button.attrib.get("size")
		if id:
			keyId = KEYIDS.get(id)
			if keyId is None:
				logMessage(LOG_ERROR, "The id '%s' appears invalid!" % id)
				continue
			if remap:
				remapId = KEYIDS.get(remap)
				if remapId is None:
					logMessage(LOG_ERROR, "The remap id '%s' appears invalid!" % remap)
					continue
				labelled = " and labelled '%s'" % label if label else ""
				titled = " and titled '%s'" % title if title else ""
				logMessage(LOG_INFORMATION, "Button '%s' (%d) remapped to '%s' (%d)%s%s." % (id, keyId, remap, remapId, labelled, titled))
		elif name:
			name = name.strip()
			try:
				dummy = int(name)
			except (TypeError, ValueError):
				if name and not name.isupper():
					logMessage(LOG_NOTE, "Auto correcting case of button name '%s' to '%s'." % (name, name.upper()))
					name = name.upper()
			if name in AUTO_CORRECT:
				logMessage(LOG_NOTE, "Auto correcting button name '%s' to '%s'." % (name, AUTO_CORRECT[name]))
				name = AUTO_CORRECT[name]
			for keyId, names in keyDescriptions[index].items():
				if names[0] == name:
					break
			else:
				logMessage(LOG_ERROR, "The keyId can't be derived from the name '%s'!" % name)
				continue
			id = KEYIDNAMES.get(keyId)
			if id is None:
				logMessage(LOG_ERROR, "The id can't be derived from the keyId '%s'!" % keyId)
				continue
		else:
			logMessage(LOG_ERROR, "The id and keyId can't be determined as the name is also undefined!")
			continue
		# print(">   Found %03d: id='%s', keyId=%d, name='%s', label='%s', pos='%s', title='%s', shape='%s', coords='%s'." % (sequence, id, keyId, name, label, pos, title, shape, coords))
		rcButtons["buttons"].append(keyId)
		rcButtons[sequence] = {}
		rcButtons[sequence]["sequence"] = sequence
		if remap:
			rcButtons[sequence]["remap"] = id
			rcButtons[sequence]["remapId"] = keyId
			rcButtons[sequence]["id"] = remap
			rcButtons[sequence]["keyId"] = remapId
		else:
			rcButtons[sequence]["id"] = id
			rcButtons[sequence]["keyId"] = keyId
		if name:
			rcButtons[sequence]["name"] = name
		if label:
			rcButtons[sequence]["label"] = label
		elif name:
			rcButtons[sequence]["label"] = name
		elif title:
			rcButtons[sequence]["label"] = title
		if pos:
			valid, newPos = checkValueList(pos, 2, "pos", keyId, id)
			if valid:
				rcButtons[sequence]["pos"] = newPos
				rcButtons[sequence]["position"] = "%03d%03d" % (newPos[1], newPos[0])
		else:
			rcButtons[sequence]["position"] = "999999"
		if title:
			rcButtons[sequence]["title"] = title
		if shape:
			shape = checkShape(shape, coords, keyId, id)
			rcButtons[sequence]["shape"] = shape
		if coords:
			if shape == "circle":
				listSize = 3
			elif shape == "poly":
				listSize = 0
			elif shape == "rect":
				listSize = 4
			valid, coords = checkValueList(coords, listSize, "coords", keyId, id)
			if valid:
				rcButtons[sequence]["coords"] = coords
		elif radius:
			valid, radius = checkValueList(radius, 1, "radius", keyId, id)
			if valid and newPos:
				rcButtons[sequence]["coords"] = [newPos[0], newPos[1], radius[0]]
		elif size:
			valid, size = checkValueList(size, 2, "size", keyId, id)
			if valid and newPos:
				xOff = int((size[0] / 2.0) + 0.5)
				yOff = int((size[1] / 2.0) + 0.5)
				rcButtons[sequence]["coords"] = [newPos[0] - xOff, newPos[1] - yOff, newPos[0] + xOff, newPos[1] + yOff]
	rcButtons["buttons"] = sorted([int(x) for x in rcButtons["buttons"]])
	return rcButtons


def formatLine(line, format):
	if line is None:
		return line
	line = line.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")
	if format == FORMAT_UNCHANGED:
		return line
	elif format == FORMAT_CAPITALISE:
		result = []
		for word in line.split(" "):
			result.append("%s%s" % (word[0].upper(), word[1:]) if word else "")
		return " ".join(result)
	return line.upper()


def checkValueList(valueList, listSize, attrib, keyId, id):
	attrib = " attribute '%s'" % attrib if attrib else ""
	msg = " in button '%s' (%d)%s" % (id, keyId, attrib)
	if isinstance(valueList, str):
		if "." in valueList:
			logMessage(LOG_ALERT, "Values%s are using '.' as a separator!" % msg)
			valueList.replace(".", ",")
		valueList = [x.strip() for x in valueList.split(",")]
	if not isinstance(valueList, (list, tuple)):
		logMessage(LOG_ALERT, "Value '%s'%s is not a comma separated list!" % (str(valueList), msg))
		return False, valueList
	size = len(valueList)
	valid = False
	try:
		checkedValueList = []
		for value in valueList:
			value = int(value)
			checkedValueList.append(value)
			if value > 500:
				logMessage(LOG_ALERT, "Value %s%s has an item value of %d which is out of the expected range!" % (str(valueList), msg, value))
		if listSize and size == listSize:
			valid = True
		elif listSize and size < listSize:
			logMessage(LOG_ALERT, "Value %s%s is shorter than expected!" % (str(valueList), msg))
		elif listSize and size > listSize:
			logMessage(LOG_ALERT, "Value %s%s is longer than expected!" % (str(valueList), msg))
		else:
			valid = True
		valueList = checkedValueList
	except (ValueError, TypeError):
		if listSize and size == listSize:
			logMessage(LOG_ALERT, "Value %s%s is invalid but is the correct length!" % (str(valueList), msg))
		elif listSize and size < listSize:
			logMessage(LOG_ALERT, "Value %s%s is invalid and shorter than expected!" % (str(valueList), msg))
		elif listSize and size > listSize:
			logMessage(LOG_ALERT, "Value %s%s is invalid and longer than expected!" % (str(valueList), msg))
	return valid, valueList


def checkShape(shape, coords, keyId, id):
	msg = " in button '%s' (%d)" % (id, keyId)
	if not shape.islower():
		logMessage(LOG_NOTE, "Auto correcting case of button shape '%s'%s to '%s'." % (shape, msg, shape.lower()))
		shape = shape.lower()
	if shape not in ("circle", "poly", "rect"):
		logMessage(LOG_ERROR, "Invalid shape '%s'%s detected!" % (shape, msg))
	newShape = None
	if coords:
		valid, data = checkValueList(coords, 0, None, keyId, id)
		if valid:
			size = len(data)
			if size == 3:
				newShape = "circle"
			elif size == 4:
				newShape = "rect"
			elif size > 5 and (size % 2) == 0:
				newShape = "poly"
		else:
			logMessage(LOG_WARNING, "Coordinates %s%s are invalid!" % (data, msg))
	if newShape and shape != newShape:
		if newShape:
			logMessage(LOG_NOTE, "Shape '%s'%s inconsistent with %d coordinates, auto correcting shape to '%s'!" % (shape, msg, size, newShape))
			shape = newShape
		else:
			logMessage(LOG_ERROR, "Shape '%s'%s inconsistent with %d coordinates!" % (shape, msg, size))
	return shape


# Sort the remote control buttons ready for output.
#
def sortButtons(sortOrder, rcButtons):
	buttonOrder = []
	nonButtons = []
	for sequence in rcButtons.keys():
		try:
			sequence = int(sequence)
			if sortOrder == SORT_SEQUENCE:
				buttonOrder.append("%04d" % sequence)
			elif sortOrder == SORT_POSITION:
				buttonOrder.append("%s%04d" % (rcButtons[sequence].get("position", "999999"), sequence))
			elif sortOrder == SORT_KEYID:
				buttonOrder.append("%04d%04d" % (rcButtons[sequence].get("keyId", 9999), sequence))
			elif sortOrder == SORT_LABEL:
				buttonOrder["%s%04d" % (rcButtons[sequence].get("label", "ZZZZZZ"), sequence)] = sequence
		except ValueError:
			nonButtons.append((sequence, rcButtons[sequence]))
	buttonList = []
	for button in sorted(buttonOrder):
		sequence = int(button[-4:])
		buttonList.append(sequence)
	for sequence in sorted(nonButtons):
		logMessage(LOG_DEBUG, "Additional data item '%s' found '%s'." % (sequence[0], sequence[1]))
	return buttonList


# Look for, and report, duplicates.
#
def findDuplicates(buttonList, rcButtons):
	for item in ("position", "id", "label"):
		values = {}
		for button in buttonList:
			value = rcButtons[button].get(item)
			if item == "id" and value == "KEY_RESERVED":  # Dont report duplicated KEY_RESERVED buttons.
				continue
			if value in values:
				if item == "id":
					logMessage(LOG_WARNING, "Button %d with id '%s' (%d) is a duplicate %s with button %d!" % (button, rcButtons[button].get("id", "Unknown"), rcButtons[button].get("keyId", 0), item, values[value]))
				elif item == "position":
					pos = "%d,%d" % (int(value[3:]), int(value[:3]))
					logMessage(LOG_WARNING, "Button %d with id '%s' (%d) is a duplicate %s (%s) with button %d with id '%s' (%d)!" % (button, rcButtons[button].get("id", "Unknown"), rcButtons[button].get("keyId", 0), item, pos, values[value], rcButtons[values[value]].get("id", "Unknown"), rcButtons[values[value]].get("keyId", 0)))
				else:
					logMessage(LOG_WARNING, "Button %d with id '%s' (%d) is a duplicate %s (%s) with button %d with id '%s' (%d)!" % (button, rcButtons[button].get("id", "Unknown"), rcButtons[button].get("keyId", 0), item, value, values[value], rcButtons[values[value]].get("id", "Unknown"), rcButtons[values[value]].get("keyId", 0)))
			else:
				values[value] = button
	return


# Create the XML button definition file.
#
def buildXML(filename, type, buttonList, rcButtons):
	xml = []
	xml.append("<rcs>")
	id = rcButtons.get("id", 2)
	image = rcButtons.get("image")
	if type == "New":
		if image:
			xml.append("\t<rc image=\"%s\">" % image)
		else:
			xml.append("\t<rc>")
	elif type == "Old":
		xml.append("\t<rc id=\"%d\">" % id)
	else:
		if image:
			xml.append("\t<rc id=\"%d\" image=\"%s\">" % (id, image))
		else:
			xml.append("\t<rc id=\"%d\">" % id)
	for button in buttonList:
		attribs = []
		id = rcButtons[button].get("id", "KEY_RESERVED")
		keyId = rcButtons[button].get("keyId", 0)
		remap = rcButtons[button].get("remap")
		if remap:
			attribs.append("id=\"%s\"" % remap)
			attribs.append("remap=\"%s\"" % id)
		elif type in ("Hybrid", "New"):
			attribs.append("id=\"%s\"" % id)
		if type in ("Hybrid", "Old"):
			attribs.append("name=\"%s\"" % rcButtons[button].get("name", ""))
		if type in ("Hybrid", "New"):
			attribs.append("label=\"%s\"" % rcButtons[button].get("label", ""))
		attribs.append("pos=\"%s\"" % ",".join([str(x) for x in rcButtons[button].get("pos", "")]))
		title = rcButtons[button].get("title", "")
		shape = rcButtons[button].get("shape", "")
		coords = rcButtons[button].get("coords", "")
		if type in ("Hybrid", "New") and title and shape and coords:
			attribs.append("title=\"%s\"" % title)
			attribs.append("shape=\"%s\"" % shape)
			attribs.append("coords=\"%s\"" % ",".join([str(x) for x in coords]))
		if type == "Old" and button < 0:
			xml.append("\t\t<!-- <button %s /> -->" % " ".join(attribs))
		else:
			xml.append("\t\t<button %s />" % " ".join(attribs))
	xml.append("\t</rc>")
	xml.append("</rcs>")
	logMessage(LOG_REPORT, "%d buttons loaded, %d buttons verified and written to %s format XML file." % (len(rcButtons.get("buttons")), len(buttonList), type.lower()))
	saveFile(filename, "-%s" % type, xml)
	return


def saveFile(filename, suffix, content):
	filename = "%s%s" % (filename, suffix)
	try:
		with open(filename, "w") as fd:
			for line in content:
				fd.write("%s\n" % line)
	except (IOError, OSError) as err:
		print("  Error %d: Writing remote control file '%s'! (%s)" % (err.errno, filename, err.strerror))
	except Exception as err:
		print("  Error: Unexpected error writing remote control file '%s'! (%s)" % (filename, err))
	return


def logMessage(level, message):
	if LOG_LEVEL >= level:
		if level == LOG_PROGRAM:
			print(message)
		elif level == LOG_REPORT:
			print("  %s" % message)
		else:
			print("    %s: %s" % (LOG_LEVELS[level], message))


# This is the mainline part of the code.
#
logMessage(LOG_PROGRAM, "ConvertRemoteControl version %s" % VERSION)
logMessage(LOG_PROGRAM, "Copyright (C) 2021  IanSav  -  All rights reserved.\n")
logMessage(LOG_PROGRAM, "This program comes with ABSOLUTELY NO WARRANTY.")
logMessage(LOG_PROGRAM, "This is free software, and you are welcome to redistribute it under")
logMessage(LOG_PROGRAM, "certain conditions.  See source code and GNUv3 for details.\n")
logMessage(LOG_PROGRAM, "Running at logging level %d (%s)." % (LOG_LEVEL, LOG_LEVELS[LOG_LEVEL]))
logMessage(LOG_PROGRAM, "Output files will be sorted in %s order." % SORT_ORDERS[SORT_ORDER])
if FORMAT_LABELS:
	logMessage(LOG_PROGRAM, "Labels will be %s." % FORMATS[FORMAT_LABELS])
if FORMAT_TITLES:
	logMessage(LOG_PROGRAM, "Titles will be %s." % FORMATS[FORMAT_TITLES])
if len(argv) > 1:
	args = argv
	args.pop(0)
else:
	args = [x for x in listdir(".") if isfile(x) and x.endswith(".xml")]
for filename in sorted(args):
	logMessage(LOG_PROGRAM, "\nProcessing remote control filename '%s'." % filename)
	rcButtons = loadRemoteXML(filename)
	buttonList = sortButtons(SORT_ORDER, rcButtons)
	findDuplicates(buttonList, rcButtons)
	buildXML(filename, "New", buttonList, rcButtons)
logMessage(LOG_PROGRAM, "\nProcessing complete.")
exit(0)
