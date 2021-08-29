#!/usr/bin/python
#
# 	CheckRemoteControl.py
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
from os.path import dirname, isfile, join as pathjoin, splitext
from sys import argv
from xml.etree.cElementTree import ParseError, parse, fromstring

from KeyBindings import keyDescriptions
from keyids import KEYIDS, invertKeyIds

VERSION = "1.10  -  12-May-2021"

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

SORT_KEYID = 0
SORT_POSITION_XML = 1
SORT_POSITION_HTML = 2
SORT_SEQUENCE_XML = 3
SORT_SEQUENCE_HTML = 4
SORT_ORDERS = [
	"keyid",
	"XML button position",
	"HTML button position",
	"XML file entry",
	"HTML file entry"
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
SORT_ORDER = SORT_SEQUENCE_XML
FORMAT_LABELS = FORMAT_CAPITALISE
FORMAT_TITLES = FORMAT_CAPITALISE
USE_ALLIANCE_PATH = False
TOLERANCE = 0

AUTO_CORRECT = {
	"CH-": "BOUQUET-",
	"CH+": "BOUQUET+",
	"CHANNEL-": "BOUQUET-",
	"CHANNEL+": "BOUQUET+",
	"CONTEXT_MENU": "CONTEXT",
	"FAVORITES": "FAV",
	"FFW": "FASTFORWARD",
	"FILELIST": "LIST",
	"FORWARD": "FASTFORWARD",
	"MODE": "VMODE",
	"NEXT": "ARROWRIGHT",
	"PREVIOUS": "ARROWLEFT",
	"PROGRAMM": "TIMER",
	"RES": "VMODE",
	"REW": "REWIND",
	"RRW": "REWIND",
	"SWITCHVIDEOMODE": "VMODE",
	"TIME": "TIMER"
}

invert = invertKeyIds()


# Load the XML specifications for the remote control.
#
def loadRemoteXML(filename, rcButtons):
	filename = "%s.xml" % filename
	logMessage(LOG_REPORT, "Loading remote control XML definition file '%s'." % filename)
	domXML = None
	rcButtons["xmlFound"] = False
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
		logMessage(LOG_WARNING, "Remote control XML is undefined so remote control id will be processed as '2'!")
		rcButtons["id"] = 2
		return rcButtons
	rc = domXML.find("rc")
	if rc is None:
		logMessage(LOG_ERROR, "Remote control XML file structure is invalid!")
		return rcButtons
	rcButtons["xmlFound"] = True
	rcButtons["xmlButtons"] = []
	id = rc.attrib.get("id")
	if id:
		msg = " but being processed as '%d'"
		if filename == "dmm0":
			index = 0
			msg = msg % index
		elif filename.startswith("dmm"):
			index = 1
			msg = msg % index
		elif filename == "xp1000":
			index = 3
			msg = msg % index
		elif filename == "formuler1":
			index = 4
			msg = msg % index
		else:
			index = 2
			msg = msg % index
		if id == str(index):
			msg = ""
		logMessage(LOG_REPORT, "Remote control id defined as '%s'%s." % (id, msg))
		rcButtons["id"] = index
	else:
		logMessage(LOG_REPORT, "Remote control id is undefined so '2' will be assumed.")
		rcButtons["id"] = 2
	image = rc.attrib.get("image")
	if image:
		if not USE_ALLIANCE_PATH and image.startswith(ALLIANCE_IMAGE_PATH):
			image = pathjoin(REMOTE_IMAGE_PATH, "%s.png" % image.split("/")[3])
		rcButtons["xmlImage"] = image
	placeHolder = 0
	found = 0
	sequence = 0
	for button in rc.findall("button"):
		found += 1
		keyName = button.attrib.get("id", button.attrib.get("keyid"))
		remap = button.attrib.get("remap")
		name = button.attrib.get("name")
		label = formatLine(button.attrib.get("label"), FORMAT_LABELS)
		pos = button.attrib.get("pos")
		title = formatLine(button.attrib.get("title"), FORMAT_TITLES)
		shape = button.attrib.get("shape")
		coords = button.attrib.get("coords")
		if keyName:
			keyId = KEYIDS.get(keyName)
			if keyId is None:
				logMessage(LOG_ERROR, "The keyName '%s' appears invalid!" % keyName)
				continue
			elif keyId == 0:
				placeHolder -= 1
				keyId = placeHolder
			if remap:
				remapId = KEYIDS.get(remap)
				if remapId is None:
					logMessage(LOG_ERROR, "The remap keyName '%s' appears invalid!" % remap)
					continue
				labelled = " and labelled '%s'" % label if label else ""
				titled = " and titled '%s'" % title if title else ""
				logMessage(LOG_INFORMATION, "Button '%s' (%d) remapped to '%s' (%d)%s%s." % (keyName, keyId, remap, remapId, labelled, titled))
				if remapId not in rcButtons:
					rcButtons[remapId] = {}
				rcButtons[remapId]["remapName"] = keyName
				rcButtons[remapId]["remapId"] = keyId
				keyName = remap
				keyId = remapId
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
			keyName = invert.get(keyId)
			if keyName is None:
				logMessage(LOG_ERROR, "The keyName can't be derived from the keyId '%s'!" % keyId)
				continue
		else:
			logMessage(LOG_ERROR, "The keyName and keyId can't be determined as the name is also undefined!")
			continue
		# print(">   Found keyId=%d, keyName='%s', name='%s', label='%s', pos='%s', title='%s', shape='%s', coords='%s'." % (keyId, keyName, name, label, pos, title, shape, coords))
		if keyId not in rcButtons:
			rcButtons[keyId] = {}
		rcButtons["xmlButtons"].append(keyId)
		rcButtons[keyId]["xmlKeyName"] = keyName
		rcButtons[keyId]["xmlKeyId"] = keyId
		sequence += 1
		rcButtons[keyId]["xmlSequence"] = "%06d" % sequence
		if name:
			rcButtons[keyId]["xmlName"] = name
		if label:
			rcButtons[keyId]["xmlLabel"] = label
		if pos:
			valid, newPos = checkValueList(pos, 2, "pos", keyId, keyName)
			if valid:
				rcButtons[keyId]["xmlPos"] = newPos
				rcButtons[keyId]["xmlPosition"] = "%06d%06d" % (newPos[1], newPos[0])
		else:
			rcButtons[keyId]["xmlPosition"] = "999999999999"
		if title:
			rcButtons[keyId]["xmlTitle"] = title
		if shape:
			shape = checkShape(shape, coords, keyId, keyName)
			rcButtons[keyId]["xmlShape"] = shape
		if coords:
			if shape == "circle":
				listSize = 3
			elif shape == "poly":
				listSize = 0
			elif shape == "rect":
				listSize = 4
			valid, coords = checkValueList(coords, listSize, "coords", keyId, keyName)
			if valid:
				rcButtons[keyId]["xmlCoords"] = coords
	rcButtons["xmlButtons"] = sorted([int(x) for x in rcButtons["xmlButtons"]])
	return rcButtons


# Load the HTML specifications for the remote control.
#
def loadRemoteHTML(filename, rcButtons):
	filename = "%s.html" % filename
	logMessage(LOG_REPORT, "Loading remote control HTML definition file '%s'." % filename)
	domHTML = None
	rcButtons["htmlFound"] = False
	try:
		with open(filename, "r") as fd:  # This open gets around a possible file handle leak in Python's XML parser.
			lines = fd.read().splitlines()
			newLines = ["<html>"]
			for line in lines:
				check = line.strip()
				if (check.startswith("<img ") or check.startswith("<area ")) and not check.endswith("/>"):
					newLines.append(line.replace(">", " />"))
				else:
					newLines.append(line)
			newLines.append("</html>")
			try:
				domHTML = fromstring("\n".join(newLines))
			except ParseError as err:
				content = newLines
				line, column = err.position
				print("  HTML Parse Error: '%s' in '%s'!" % (err, filename))
				data = content[line - 1].replace("\t", " ").rstrip()
				print("  HTML Parse Error: '%s'" % data)
				print("  HTML Parse Error: '%s^%s'" % ("-" * column, " " * (len(data) - column - 1)))
			except Exception as err:
				print("  Error: Unable to parse HTML remote control data in '%s' - '%s'!" % (filename, err))
	except (IOError, OSError) as err:
		if err.errno == ENOENT:  # No such file or directory
			print("  Warning: Remote control HTML file '%s' does not exist!" % filename)
		else:
			print("  Error %d: Opening remote control HTML file '%s'! (%s)" % (err.errno, filename, err.strerror))
	except Exception as err:
		print("  Error: Unexpected error opening remote control HTML file '%s'! (%s)" % (filename, err))
	if domHTML is None:
		logMessage(LOG_WARNING, "Remote control HTML is undefined!")
		return rcButtons
	img = domHTML.find("img")
	if img is None:
		logMessage(LOG_ERROR, "No remote control image found in HTML file!")
	else:
		image = img.attrib.get("src")
		if image:
			if not USE_ALLIANCE_PATH and image.startswith(ALLIANCE_IMAGE_PATH):
				image = pathjoin(REMOTE_IMAGE_PATH, "%s.png" % image.split("/")[3])
			rcButtons["htmlImage"] = image
	map = domHTML.find("map")
	if map is None:
		logMessage(LOG_ERROR, "Remote control HTML file structure is invalid!")
		return rcButtons
	rcButtons["htmlFound"] = True
	rcButtons["htmlButtons"] = []
	placeHolder = 0
	sequence = 0
	for area in map.findall("area"):
		keyId = area.attrib.get("onclick", "").replace("pressMenuRemote(", "").replace(");", "").replace("'", "")
		if keyId:
			keyId = int(keyId)
			keyName = invert.get(keyId)
			if keyName is None:
				logMessage(LOG_ERROR, "The keyName can't be derived from the keyId '%s'!" % keyId)
		else:
			placeHolder -= 1
			keyId = placeHolder
			keyName = "KEY_RESERVED"
		title = formatLine(area.attrib.get("title"), FORMAT_TITLES)
		alt = formatLine(area.attrib.get("alt"), FORMAT_TITLES)
		if title and alt and title != alt:
			logMessage(LOG_NOTE, "Button '%s' (%d) has both 'title' and 'alt' attributes but they are different!  ('%s' != '%s')" % (keyName, keyId, title, alt))
		if title is None and alt:
			logMessage(LOG_NOTE, "Button '%s' (%d) has no 'title' attribute, using 'alt' instead." % (keyName, keyId))
			title = alt
		shape = area.attrib.get("shape")
		coords = area.attrib.get("coords")
		onclick = area.attrib.get("onclick")
		# print(">   Found keyId=%d, keyName='%s', title='%s', shape='%s', coords='%s', onclick='%s'." % (keyId, keyName, title, shape, coords, onclick))
		if keyId not in rcButtons:
			rcButtons[keyId] = {}
		rcButtons["htmlButtons"].append(keyId)
		sequence += 1
		rcButtons[keyId]["htmlSequence"] = "%06d" % sequence
		rcButtons[keyId]["htmlKeyName"] = keyName
		rcButtons[keyId]["htmlKeyId"] = keyId
		if title:
			rcButtons[keyId]["htmlTitle"] = title
		if shape:
			shape = checkShape(shape, coords, keyId, keyName)
			rcButtons[keyId]["htmlShape"] = shape
		if coords:
			if shape == "circle":
				listSize = 3
			elif shape == "poly":
				listSize = 0
			elif shape == "rect":
				listSize = 4
			valid, coords = checkValueList(coords, listSize, "coords", keyId, keyName)
			if valid:
				rcButtons[keyId]["htmlCoords"] = coords
		# if shape == "circle":
		# 	pos = [coords[0], coords[1]]
		# elif shape == "poly":
		# 	count = len(coords)
		# 	pos = [0, 0]
		# 	for index in range(count, 2):
		# 		pos[0] += coords[index]
		# 		pos[1] += coords[index + 1]
		# 	pos = [int(round(pos[0] * 2 / count)), int(round(pos[1] * 2 / count))]
		# elif shape == "rect":
		# 	pos = [coords[0] + int(round((coords[2] - coords[0]) / 2)), coords[1] + int(round((coords[3] - coords[1]) / 2))]
		# else:
		# 	pos = None
		# if pos:
		# 	valid, pos = checkValueList(pos, 2, "pos", keyId, keyName)
		# 	if valid:
		# 		logMessage(LOG_NOTE, "Remote control keyid %s (%d) attribute 'pos' with a value of %s is being added." % (keyName, keyId, str(pos)))
		# 		rcButtons[keyId]["htmlPos"] = pos
		# 		rcButtons[keyId]["htmlPosition"] = "%06d%06d" % (pos[1], pos[0])
		if keyId > 0:
			onClick = "pressMenuRemote('%s');" % keyId
			if onclick != onClick:
				logMessage(LOG_NOTE, "Auto correcting format of onclick '%s' to '%s'." % (onclick, onClick))
				onclick = onClick
			rcButtons[keyId]["htmlOnclick"] = onclick
	rcButtons["htmlButtons"] = sorted([int(x) for x in rcButtons["htmlButtons"]])
	return rcButtons


def formatLine(line, format):
	if line is None or format == FORMAT_UNCHANGED:
		return line
	elif format == FORMAT_CAPITALISE:
		result = []
		for word in line.split(" "):
			result.append("%s%s" % (word[0].upper(), word[1:]) if word else "")
		return " ".join(result)
	return line.upper()


def checkValueList(valueList, listSize, attrib, keyId, keyName):
	attrib = " attribute '%s'" % attrib if attrib else ""
	msg = " in button '%s' (%d)%s" % (keyName, keyId, attrib)
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


def checkShape(shape, coords, keyId, keyName):
	msg = " in button '%s' (%d)" % (keyName, keyId)
	if not shape.islower():
		logMessage(LOG_NOTE, "Auto correcting case of button shape '%s'%s to '%s'." % (shape, msg, shape.lower()))
		shape = shape.lower()
	if shape not in ("circle", "poly", "rect"):
		logMessage(LOG_ERROR, "Invalid shape '%s'%s detected!" % (shape, msg))
	newShape = None
	if coords:
		valid, data = checkValueList(coords, 0, None, keyId, keyName)
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
	buttonOrder = {}
	nonButtons = []
	for keyId in rcButtons.keys():
		try:
			keyId = int(keyId)
			if sortOrder == SORT_KEYID:
				buttonOrder["%06d" % keyId] = keyId
			elif sortOrder == SORT_POSITION_XML:
				buttonOrder[rcButtons[keyId].get("xmlPosition", "999999999999")] = keyId
			elif sortOrder == SORT_POSITION_HTML:
				buttonOrder[rcButtons[keyId].get("htmlPosition", "999999999999")] = keyId
			elif sortOrder == SORT_SEQUENCE_XML:
				buttonOrder[rcButtons[keyId].get("xmlSequence", "999999")] = keyId
			elif sortOrder == SORT_SEQUENCE_HTML:
				buttonOrder[rcButtons[keyId].get("htmlSequence", "999999")] = keyId
		except ValueError:
			nonButtons.append((keyId, rcButtons[keyId]))
	keyIds = []
	for keyId in sorted(buttonOrder.keys()):
		keyIds.append(buttonOrder[keyId])
	for keyId in sorted(nonButtons):
		logMessage(LOG_DEBUG, "Additional data item '%s' found '%s'." % (keyId[0], keyId[1]))
	return keyIds


# Compare the image and list of buttons defined in the XML and HTML files.
#
def compareRemotes(filename, rcButtons):
	imageMatch = True
	if "xmlImage" in rcButtons and "htmlImage" in rcButtons:
		if rcButtons["xmlImage"] == rcButtons["htmlImage"]:
			rcButtons["image"] = rcButtons["xmlImage"]
		else:
			logMessage(LOG_ALERT, "Remote control XML image value doesn't match HTML value!  ('%s' != '%s')" % (rcButtons["xmlImage"], rcButtons["htmlImage"]))
			rcButtons["image"] = rcButtons["htmlImage"]
			imageMatch = False
	elif "xmlImage" in rcButtons:
		rcButtons["image"] = rcButtons["xmlImage"]
	elif "htmlImage" in rcButtons:
		rcButtons["image"] = rcButtons["htmlImage"]
	else:
		logMessage(LOG_ERROR, "No image reference can be found for this remote control!")
		if isfile("%s.png" % filename):
			logMessage(LOG_INFORMATION, "An image file for this remote control appears to be available.")
		imageMatch = False
	xmlDiffs = []
	htmlDiffs = []
	if "xmlButtons" in rcButtons and "htmlButtons" in rcButtons:
		# This creates a single differences list.  I think the individual differences will be more helpful.
		# diffs = list(set(rcButtons["xmlButtons"]).symmetric_difference(set(rcButtons["htmlButtons"])))
		# if diffs:
		# 	msgs = []
		# 	for keyId in sorted(diffs):
		# 		msgs.append("Button keyid '%s' (%d)." % (invert.get(keyId, "*Undefined*"), keyId))
		# 	logMessage(LOG_ERROR, "The sets of buttons differ between the XML and HTML files!\n\t%s" % "\n\t".join(msgs))
		xmlDiffs = list(set(rcButtons["xmlButtons"]) - set(rcButtons["htmlButtons"]))
		if xmlDiffs:
			rcButtons["xmlOnly"] = xmlDiffs
			msgs = []
			for keyId in sorted(xmlDiffs):
				msgs.append("Button keyid '%s' (%d) named '%s'." % (rcButtons[keyId].get("xmlKeyName", "*Undefined*"), keyId, rcButtons[keyId].get("xmlName", "*Undefined*")))
			logMessage(LOG_ERROR, "These buttons are in the XML file but not the HTML file!\n\t%s" % "\n\t".join(msgs))
		htmlDiffs = list(set(rcButtons["htmlButtons"]) - set(rcButtons["xmlButtons"]))
		if htmlDiffs:
			rcButtons["htmlOnly"] = htmlDiffs
			msgs = []
			for keyId in sorted(htmlDiffs):
				msgs.append("Button keyid '%s' (%d) titled '%s'." % (rcButtons[keyId].get("htmlKeyName", "*Undefined*"), keyId, rcButtons[keyId].get("htmlTitle", "*Undefined*")))
			logMessage(LOG_ERROR, "These buttons are in the HTML file but not the XML file!\n\t%s" % "\n\t".join(msgs))
	if xmlDiffs or htmlDiffs:
		logMessage(LOG_ERROR, "Remote control XML and HTML buttons are mismatched so the validation is incomplete and may be in inaccurate!")
	rcButtons["xmlOnly"] = xmlDiffs
	rcButtons["htmlOnly"] = htmlDiffs
	return imageMatch and xmlDiffs + htmlDiffs == []


# Compare the XML and HTML versions of the remote control buttons.
#
def compareButtons(keyIds, rcButtons):
	for keyId in keyIds:
		keyName = invert.get(keyId)
		for attrib in ["keyName", "keyId", "name", "label", "pos", "title", "shape", "coords", "onclick"]:
			xmlAttrib = "xml%s%s" % (attrib[0].upper(), attrib[1:])
			htmlAttrib = "html%s%s" % (attrib[0].upper(), attrib[1:])
			if xmlAttrib in rcButtons[keyId] and htmlAttrib in rcButtons[keyId]:
				if rcButtons[keyId][xmlAttrib] == rcButtons[keyId][htmlAttrib]:
					rcButtons[keyId][attrib] = rcButtons[keyId][xmlAttrib]
				else:
					logMessage(LOG_WARNING, "Remote control keyid %s (%d) XML '%s' value doesn't match HTML value!  ('%s' != '%s')" % (keyName, keyId, attrib, rcButtons[keyId][xmlAttrib], rcButtons[keyId][htmlAttrib]))
					if attrib == "pos":
						rcButtons[keyId][attrib] = rcButtons[keyId][xmlAttrib]
					else:
						rcButtons[keyId][attrib] = rcButtons[keyId][htmlAttrib]
			elif xmlAttrib in rcButtons[keyId]:
				rcButtons[keyId][attrib] = rcButtons[keyId][xmlAttrib]
			elif htmlAttrib in rcButtons[keyId]:
				rcButtons[keyId][attrib] = rcButtons[keyId][htmlAttrib]
			if attrib in ("label", "title") and rcButtons[keyId].get(attrib):
				rcButtons[keyId][attrib] = rcButtons[keyId][attrib].replace("<", "&lt;").replace(">", "&gt;")
		shape = rcButtons[keyId].get("shape")
		pos = rcButtons[keyId].get("pos")
		coords = rcButtons[keyId].get("coords")
		axes = ["X axis", "Y axis"]
		errors = []
		if shape == "circle" and pos and coords:
			center = [coords[0], coords[1]]
			for index, axis in enumerate(axes):
				if abs(pos[index] - center[index]) > TOLERANCE:
					errors.append(axis)
		elif shape == "poly" and pos and coords:
			count = len(coords)
			center = [0, 0]
			for index in range(count, 2):
				center[0] += coords[index]
				center[1] += coords[index + 1]
			center = [int(round(center[0] * 2 / count)), int(round(center[1] * 2 / count))]
			for index, axis in enumerate(axes):
				if abs(pos[index] - center[index]) > TOLERANCE:
					errors.append(axis)
		elif shape == "rect" and pos and coords:
			center = [coords[0] + int(round((coords[2] - coords[0]) / 2)), coords[1] + int(round((coords[3] - coords[1]) / 2))]
			for index, axis in enumerate(axes):
				if abs(pos[index] - center[index]) > TOLERANCE:
					errors.append(axis)
		if errors:
			msg = "%s value exceeds" if len(errors) == 1 else "%s values exceed"
			msg = msg % " and ".join(errors)
			logMessage(LOG_WARNING, "Remote control keyid %s (%d) %s tolerance of %d pixel%s!  (shape='%s' pos=%s coords=%s center=%s)" % (keyName, keyId, msg, TOLERANCE, "" if TOLERANCE == 1 else "s", shape, pos, coords, center))
	return rcButtons


# Complete any missing attributes that can be derived from other attributes.
#
def completeAttributes(keyIds, rcButtons):
	for keyId in keyIds:
		keyName = rcButtons[keyId].get("keyName")
		name = rcButtons[keyId].get("name")
		label = rcButtons[keyId].get("label")
		title = rcButtons[keyId].get("title")
		pos = rcButtons[keyId].get("pos")
		shape = rcButtons[keyId].get("shape")
		coords = rcButtons[keyId].get("coords")
		if name is None and keyId > 0:
			if label:
				name = label.upper()
			elif title:
				name = title.upper()
			logMessage(LOG_NOTE, "Remote control keyid %s (%d) attribute 'name' with a value of '%s' is being added." % (keyName, keyId, name))
			rcButtons[keyId]["name"] = name
		if label is None:
			if name:
				label = formatLine(name, FORMAT_LABELS)
			elif title:
				label = formatLine(title, FORMAT_LABELS)
			logMessage(LOG_NOTE, "Remote control keyid %s (%d) attribute 'label' with a value of '%s' is being added." % (keyName, keyId, label))
			rcButtons[keyId]["label"] = label
		if title is None:
			if label:
				title = formatLine(label, FORMAT_TITLES)
			elif name:
				title = formatLine(name, FORMAT_TITLES)
			logMessage(LOG_NOTE, "Remote control keyid %s (%d) attribute 'title' with a value of '%s' is being added." % (keyName, keyId, title))
			rcButtons[keyId]["title"] = title
		if pos is None and coords:
			if shape == "circle":
				pos = [coords[0], coords[1]]
			elif shape == "poly":
				count = len(coords)
				pos = [0, 0]
				for index in range(count, 2):
					pos[0] += coords[index]
					pos[1] += coords[index + 1]
				pos = [int(round(pos[0] * 2 / count)), int(round(pos[1] * 2 / count))]
			elif shape == "rect":
				pos = [coords[0] + int(round((coords[2] - coords[0]) / 2)), coords[1] + int(round((coords[3] - coords[1]) / 2))]
			logMessage(LOG_NOTE, "Remote control keyid %s (%d) attribute 'pos' with a value of %s is being added." % (keyName, keyId, str(pos)))
			rcButtons[keyId]["pos"] = pos
		if coords is None and pos:
			if shape == "circle":
				coords = [pos[0], pos[1], 12]
			elif shape == "poly":
				coords = [pos[0] - 6, pos[1], pos[0], pos[1] - 6, pos[0] + 6, pos[1], pos[0] + 6]
			elif shape == "rect":
				coords = [pos[0] - 6, pos[1] - 6, pos[0] + 6, pos[1] + 6]
			logMessage(LOG_NOTE, "Remote control keyid %s (%d) attribute 'coords' with a value of %s is being added." % (keyName, keyId, str(coords)))
			rcButtons[keyId]["pos"] = coords
	return rcButtons


# Create the XML button definition file.
#
def buildXML(filename, type, keyIds, rcButtons):
	xml = []
	xml.append("<rcs>")
	if type == "New":
		xml.append("\t<rc image=\"%s\">" % rcButtons.get("image"))
	elif type == "Old":
		xml.append("\t<rc id=\"%d\">" % rcButtons.get("id", 2))
	else:
		xml.append("\t<rc id=\"%d\" image=\"%s\">" % (rcButtons.get("id", 2), rcButtons.get("image")))
	for key in keyIds:
		value = rcButtons[key]
		attribs = []
		keyName = value.get("keyName", "KEY_RESERVED")
		keyId = value.get("keyId", 0)
		if key != keyId:
			logMessage(LOG_ERROR, "Sort key '%d' does not match the key id '%d'!" % (key, keyId))
		remapName = value.get("remapName")
		if remapName:
			attribs.append("id=\"%s\"" % remapName)
			attribs.append("remap=\"%s\"" % keyName)
		elif type in ("Hybrid", "New"):
			attribs.append("id=\"%s\"" % keyName)
		if type in ("Hybrid", "Old"):
			attribs.append("name=\"%s\"" % value.get("name", ""))
		if type in ("Hybrid", "New"):
			attribs.append("label=\"%s\"" % value.get("label", ""))
		attribs.append("pos=\"%s\"" % ",".join([str(x) for x in value.get("pos", "")]))
		if type in ("Hybrid", "New"):
			attribs.append("title=\"%s\"" % value.get("title", ""))
			attribs.append("shape=\"%s\"" % value.get("shape", ""))
			attribs.append("coords=\"%s\"" % ",".join([str(x) for x in value.get("coords", "")]))
		if type == "Old" and key < 0:
			xml.append("\t\t<!-- <button %s /> -->" % " ".join(attribs))
		else:
			xml.append("\t\t<button %s />" % " ".join(attribs))
	xml.append("\t</rc>")
	xml.append("</rcs>")
	logMessage(LOG_REPORT, "%d buttons found and written to %s format XML file." % (len(keyIds), type.lower()))
	saveFile(filename, ".xml-%s" % type, xml)
	return


# Create the new format XML button definition file.
#
def buildHTML(filename, keyIds, rcButtons):
	html = []
	html.append("<img border=\"0\" src=\"%s\" usemap=\"#map\" />" % rcButtons.get("image", ""))
	html.append("<map name=\"map\">")
	for key in keyIds:
		value = rcButtons[key]
		attribs = []
		keyName = value.get("keyName", "KEY_RESERVED")
		keyId = value.get("keyId", 0)
		if key != keyId:
			logMessage(LOG_ERROR, "Sort key '%d' does not match the key id '%d'!" % (key, keyId))
		attribs.append("title=\"%s\"" % value.get("title", ""))
		attribs.append("shape=\"%s\"" % value.get("shape", ""))
		attribs.append("coords=\"%s\"" % ",".join([str(x) for x in value.get("coords", "")]))
		if key > 0:
			attribs.append("onclick=\"pressMenuRemote('%d');\"" % keyId)
		html.append("\t<area %s />" % " ".join(attribs))
	html.append("</map>")
	logMessage(LOG_REPORT, "%d buttons found and written to HTML file." % len(keyIds))
	saveFile(filename, ".html-New", html)
	return


def saveFile(filename, suffix, content):
	# print("\n".join(content))
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
logMessage(LOG_PROGRAM, "CheckRemoteControl version %s" % VERSION)
logMessage(LOG_PROGRAM, "Copyright (C) 2021  IanSav  -  All rights reserved.\n")
logMessage(LOG_PROGRAM, "This program comes with ABSOLUTELY NO WARRANTY.")
logMessage(LOG_PROGRAM, "This is free software, and you are welcome to redistribute it under")
logMessage(LOG_PROGRAM, "certain conditions.  See source code and GNUv3 for details.\n")
logMessage(LOG_PROGRAM, "Running at logging level %d (%s)." % (LOG_LEVEL, LOG_LEVELS[LOG_LEVEL]))
logMessage(LOG_PROGRAM, "Output files will be sorted in %s order." % SORT_ORDERS[SORT_ORDER])
if FORMAT_LABELS:
	logMessage(LOG_PROGRAM, "XML labels will be %s." % FORMATS[FORMAT_LABELS])
if FORMAT_TITLES:
	logMessage(LOG_PROGRAM, "HTML titles will be %s." % FORMATS[FORMAT_TITLES])
logMessage(LOG_PROGRAM, "If both XML and HTML data is valid but different the HTML attributes will be used except for 'pos'.\n")
filenames = set()
if len(argv) > 1:
	args = argv
	args.pop(0)
else:
	args = [x for x in listdir(".") if isfile(x)]
for filename in args:
	if filename.endswith(".png") or filename.endswith(".xml") or filename.endswith(".html"):
		if filename.startswith("ini5") or filename.startswith("ini7") or filename.startswith("beyonwiz"):
			continue  # Don't process Beyonwiz remote controls yet.
		filenames.add(splitext(filename)[0])
	elif splitext(filename)[1] == "":
		filenames.add(filename)
# filenames = ["0test", "zgemma3"]
for filename in sorted(filenames):
	logMessage(LOG_PROGRAM, "Processing remote control filename '%s'." % filename)
	rcButtons = {}
	rcButtons = loadRemoteXML(filename, rcButtons)  # Load the XML specifications for the remote control.
	rcButtons = loadRemoteHTML(filename, rcButtons)  # Load the HTML specifications for the remote control.
	comparable = compareRemotes(filename, rcButtons)  # Compare the image and list of buttons defined in the XML and HTML files.
	keyIds = sortButtons(SORT_ORDER, rcButtons)  # Sort the remote control buttons ready for output.
	rcButtons = compareButtons(keyIds, rcButtons)  # Compare the XML and HTML versions of the remote control.
	rcButtons = completeAttributes(keyIds, rcButtons)  # Complete any missing attributes that can be derived from other attributes.
	if comparable:
		# if filename in ["0test", "zgemma3"]:
		# 	print(keyIds)
		# 	for key in keyIds:
		# 		if isinstance(rcButtons[key], dict):
		# 			for item in sorted(rcButtons[key].keys()):
		# 				print(key, item, rcButtons[key][item])
		# 		else:
		# 			print(key, rcButtons[key])
		buildXML(filename, "Old", keyIds, rcButtons)  # Create the old format XML button definition file.
		buildXML(filename, "New", keyIds, rcButtons)  # Create the new format XML button definition file.
		buildXML(filename, "Hybrid", keyIds, rcButtons)  # Create the hybrid format XML button definition file.
		buildHTML(filename, keyIds, rcButtons)  # Create the HTML button definition file.
	logMessage(LOG_PROGRAM, "")
logMessage(LOG_PROGRAM, "Processing complete.")
exit(0)
