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

VERSION = "1.21  -  16-Aug-2022"

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

REMOTE_IMAGE_PATH = "/images/remotes/"

LOG_LEVEL = LOG_INFORMATION
SORT_ORDER = SORT_POSITION
FORMAT_LABELS = FORMAT_CAPITALISE
FORMAT_TITLES = FORMAT_CAPITALISE

KEYIDS = {
	"KEY_RESERVED": 0,
	"KEY_ESC": 1,
	"KEY_1": 2,
	"KEY_2": 3,
	"KEY_3": 4,
	"KEY_4": 5,
	"KEY_5": 6,
	"KEY_6": 7,
	"KEY_7": 8,
	"KEY_8": 9,
	"KEY_9": 10,
	"KEY_0": 11,
	"KEY_MINUS": 12,
	"KEY_EQUAL": 13,
	"KEY_BACKSPACE": 14,
	"KEY_TAB": 15,
	"KEY_Q": 16,
	"KEY_W": 17,
	"KEY_E": 18,
	"KEY_R": 19,
	"KEY_T": 20,
	"KEY_Y": 21,
	"KEY_U": 22,
	"KEY_I": 23,
	"KEY_O": 24,
	"KEY_P": 25,
	"KEY_LEFTBRACE": 26,
	"KEY_RIGHTBRACE": 27,
	"KEY_ENTER": 28,
	"KEY_LEFTCTRL": 29,
	"KEY_A": 30,
	"KEY_S": 31,
	"KEY_D": 32,
	"KEY_F": 33,
	"KEY_G": 34,
	"KEY_H": 35,
	"KEY_J": 36,
	"KEY_K": 37,
	"KEY_L": 38,
	"KEY_SEMICOLON": 39,
	"KEY_APOSTROPHE": 40,
	"KEY_GRAVE": 41,
	"KEY_LEFTSHIFT": 42,
	"KEY_BACKSLASH": 43,
	"KEY_Z": 44,
	"KEY_X": 45,
	"KEY_C": 46,
	"KEY_V": 47,
	"KEY_B": 48,
	"KEY_N": 49,
	"KEY_M": 50,
	"KEY_COMMA": 51,
	"KEY_DOT": 52,
	"KEY_SLASH": 53,
	"KEY_RIGHTSHIFT": 54,
	"KEY_KPASTERISK": 55,
	"KEY_LEFTALT": 56,
	"KEY_SPACE": 57,
	"KEY_CAPSLOCK": 58,
	"KEY_F1": 59,
	"KEY_F2": 60,
	"KEY_F3": 61,
	"KEY_F4": 62,
	"KEY_F5": 63,
	"KEY_F6": 64,
	"KEY_F7": 65,
	"KEY_F8": 66,
	"KEY_F9": 67,
	"KEY_F10": 68,
	"KEY_NUMLOCK": 69,
	"KEY_SCROLLLOCK": 70,
	"KEY_KP7": 71,
	"KEY_KP8": 72,
	"KEY_KP9": 73,
	"KEY_KPMINUS": 74,
	"KEY_KP4": 75,
	"KEY_KP5": 76,
	"KEY_KP6": 77,
	"KEY_KPPLUS": 78,
	"KEY_KP1": 79,
	"KEY_KP2": 80,
	"KEY_KP3": 81,
	"KEY_KP0": 82,
	"KEY_KPDOT": 83,
	"KEY_103RD": 84,
	"KEY_F13": 85,
	"KEY_102ND": 86,
	"KEY_F11": 87,
	"KEY_F12": 88,
	"KEY_F14": 89,
	"KEY_F15": 90,
	"KEY_F16": 91,
	"KEY_F17": 92,
	"KEY_F18": 93,
	"KEY_F19": 94,
	"KEY_F20": 95,
	"KEY_KPENTER": 96,
	"KEY_RIGHTCTRL": 97,
	"KEY_KPSLASH": 98,
	"KEY_SYSRQ": 99,
	"KEY_RIGHTALT": 100,
	"KEY_LINEFEED": 101,
	"KEY_HOME": 102,
	"KEY_UP": 103,
	"KEY_PAGEUP": 104,
	"KEY_LEFT": 105,
	"KEY_RIGHT": 106,
	"KEY_END": 107,
	"KEY_DOWN": 108,
	"KEY_PAGEDOWN": 109,
	"KEY_INSERT": 110,
	"KEY_DELETE": 111,
	"KEY_MACRO": 112,
	"KEY_MUTE": 113,
	"KEY_VOLUMEDOWN": 114,
	"KEY_VOLUMEUP": 115,
	"KEY_POWER": 116,
	"KEY_KPEQUAL": 117,
	"KEY_KPPLUSMINUS": 118,
	"KEY_PAUSE": 119,
	"KEY_F21": 120,
	"KEY_F22": 121,
	"KEY_F23": 122,
	"KEY_F24": 123,
	"KEY_KPCOMMA": 124,
	"KEY_LEFTMETA": 125,
	"KEY_RIGHTMETA": 126,
	"KEY_COMPOSE": 127,
	"KEY_STOP": 128,
	"KEY_AGAIN": 129,
	"KEY_PROPS": 130,
	"KEY_UNDO": 131,
	"KEY_FRONT": 132,
	"KEY_COPY": 133,
	"KEY_OPEN": 134,
	"KEY_PASTE": 135,
	"KEY_FIND": 136,
	"KEY_CUT": 137,
	"KEY_HELP": 138,
	"KEY_MENU": 139,
	"KEY_CALC": 140,
	"KEY_SETUP": 141,
	"KEY_SLEEP": 142,
	"KEY_WAKEUP": 143,
	"KEY_FILE": 144,
	"KEY_SENDFILE": 145,
	"KEY_DELETEFILE": 146,
	"KEY_XFER": 147,
	"KEY_PROG1": 148,
	"KEY_PROG2": 149,
	"KEY_WWW": 150,
	"KEY_MSDOS": 151,
	"KEY_COFFEE": 152,
	"KEY_DIRECTION": 153,
	"KEY_CYCLEWINDOWS": 154,
	"KEY_MAIL": 155,
	"KEY_BOOKMARKS": 156,
	"KEY_COMPUTER": 157,
	"KEY_BACK": 158,
	"KEY_FORWARD": 159,
	"KEY_CLOSECD": 160,
	"KEY_EJECTCD": 161,
	"KEY_EJECTCLOSECD": 162,
	"KEY_NEXTSONG": 163,
	"KEY_PLAYPAUSE": 164,
	"KEY_PREVIOUSSONG": 165,
	"KEY_STOPCD": 166,
	"KEY_RECORD": 167,
	"KEY_REWIND": 168,
	"KEY_PHONE": 169,
	"KEY_ISO": 170,
	"KEY_CONFIG": 171,
	"KEY_HOMEPAGE": 172,
	"KEY_REFRESH": 173,
	"KEY_EXIT": 174,
	"KEY_MOVE": 175,
	"KEY_EDIT": 176,
	"KEY_SCROLLUP": 177,
	"KEY_SCROLLDOWN": 178,
	"KEY_KPLEFTPAREN": 179,
	"KEY_KPRIGHTPAREN": 180,
	"KEY_INTL1": 181,
	"KEY_INTL2": 182,
	"KEY_INTL3": 183,
	"KEY_INTL4": 184,
	"KEY_INTL5": 185,
	"KEY_INTL6": 186,
	"KEY_INTL7": 187,
	"KEY_INTL8": 188,
	"KEY_INTL9": 189,
	"KEY_LANG1": 190,
	"KEY_LANG2": 191,
	"KEY_LANG3": 192,
	"KEY_LANG4": 193,
	"KEY_LANG5": 194,
	"KEY_LANG6": 195,
	"KEY_LANG7": 196,
	"KEY_LANG8": 197,
	"KEY_LANG9": 198,
	"KEY_PLAYCD": 200,
	"KEY_PAUSECD": 201,
	"KEY_PROG3": 202,
	"KEY_PROG4": 203,
	"KEY_SUSPEND": 205,
	"KEY_CLOSE": 206,
	"KEY_PLAY": 207,
	"KEY_FASTFORWARD": 208,
	"KEY_BASSBOOST": 209,
	"KEY_PRINT": 210,
	"KEY_HP": 211,
	"KEY_CAMERA": 212,
	"KEY_SOUND": 213,
	"KEY_QUESTION": 214,
	"KEY_EMAIL": 215,
	"KEY_CHAT": 216,
	"KEY_SEARCH": 217,
	"KEY_CONNECT": 218,
	"KEY_FINANCE": 219,
	"KEY_SPORT": 220,
	"KEY_SHOP": 221,
	"KEY_ALTERASE": 222,
	"KEY_CANCEL": 223,
	"KEY_BRIGHTNESSDOWN": 224,
	"KEY_BRIGHTNESSUP": 225,
	"KEY_MEDIA": 226,
	"KEY_VMODE": 227,  # Deprecated, retained for backwards compatibility.
	"KEY_SWITCHVIDEOMODE": 227,
	"KEY_LAN": 238,
	"KEY_UNKNOWN": 240,
	"BTN_0": 256,
	"BTN_1": 257,
	"BtnA": 304,
	"BtnB": 305,
	"BtnC": 306,
	"BtnX": 307,
	"BtnY": 308,
	"BtnZ": 309,
	"BtnTL": 310,
	"BtnTR": 311,
	"BtnTL2": 312,
	"BtnTR2": 313,
	"BtnSelect": 314,
	"BtnStart": 315,
	"KEY_SHIFT": 351,  # This is not a transmitted key but rather a place holder for remote controls that have a SHIFT function.
	"KEY_OK": 352,
	"KEY_SELECT": 353,
	"KEY_GOTO": 354,
	"KEY_CLEAR": 355,
	"KEY_POWER2": 356,
	"KEY_OPTION": 357,
	"KEY_INFO": 358,
	"KEY_TIME": 359,
	"KEY_VENDOR": 360,
	"KEY_ARCHIVE": 361,
	"KEY_PROGRAM": 362,
	"KEY_CHANNEL": 363,
	"KEY_FAVORITES": 364,
	"KEY_EPG": 365,
	"KEY_PVR": 366,
	"KEY_MHP": 367,
	"KEY_LANGUAGE": 368,
	"KEY_TITLE": 369,
	"KEY_SUBTITLE": 370,
	"KEY_ANGLE": 371,
	"KEY_ZOOM": 372,
	"KEY_MODE": 373,
	"KEY_KEYBOARD": 374,
	"KEY_SCREEN": 375,
	"KEY_PC": 376,
	"KEY_TV": 377,
	"KEY_TV2": 378,
	"KEY_VCR": 379,
	"KEY_VCR2": 380,
	"KEY_SAT": 381,
	"KEY_SAT2": 382,
	"KEY_CD": 383,
	"KEY_TAPE": 384,
	"KEY_RADIO": 385,
	"KEY_TUNER": 386,
	"KEY_PLAYER": 387,
	"KEY_TEXT": 388,
	"KEY_DVD": 389,
	"KEY_AUX": 390,
	"KEY_MP3": 391,
	"KEY_AUDIO": 392,
	"KEY_VIDEO": 393,
	"KEY_DIRECTORY": 394,
	"KEY_LIST": 395,
	"KEY_MEMO": 396,
	"KEY_CALENDAR": 397,
	"KEY_RED": 398,
	"KEY_GREEN": 399,
	"KEY_YELLOW": 400,
	"KEY_BLUE": 401,
	"KEY_CHANNELUP": 402,
	"KEY_CHANNELDOWN": 403,
	"KEY_FIRST": 404,
	"KEY_LAST": 405,
	"KEY_AB": 406,
	"KEY_NEXT": 407,
	"KEY_RESTART": 408,
	"KEY_SLOW": 409,
	"KEY_SHUFFLE": 410,
	"KEY_BREAK": 411,
	"KEY_PREVIOUS": 412,
	"KEY_DIGITS": 413,
	"KEY_TEEN": 414,
	"KEY_TWEN": 415,
	"KEY_CONTEXT_MENU": 438,
	"KEY_DEL_EOL": 448,
	"KEY_DEL_EOS": 449,
	"KEY_INS_LINE": 450,
	"KEY_DEL_LINE": 451,
	"KEY_ASCII": 510,
	"KEY_MAX": 511,
	"KEY_TOUCHPAD_TOGGLE": 530,
	"KEY_MOUSE": 530,
	"KEY_VOD": 627
}

KNOWN_ALISAES = {
	227: ("KEY_SWITCHVIDEOMODE", "KEY_VMODE"),
	530: ("KEY_MOUSE", "KEY_TOUCHPAD_TOGGLE")
}

def invertKeyIds():
	invKeyIds = {}
	for key, value in KEYIDS.items():
		if value not in invKeyIds:
			invKeyIds[value] = key
		else:
			if value in KNOWN_ALISAES and key in KNOWN_ALISAES[value]:
				invKeyIds[value] = KNOWN_ALISAES[value][0]
			else:
				print("[keyids] Error: Key code %d is mapped to both '%s' and '%s'!" % (value, invKeyIds[value], key))
	return invKeyIds


KEYIDNAMES = invertKeyIds()

KEYDESCRIPTIONS = [{  # id=0 - dmm0 remote directory, DM8000.
	# However, the dmm0 rcpositions.xml file should define
	# an <rc id=0 /> element, but it does not, it only has
	# an <rc id=2 /> element.
	#
	# The rcpositions.xml file defines <button/> elements,
	# but they do not appear to emit codes.
	KEYIDS["BTN_0"]: ("UP", "fp"),
	KEYIDS["BTN_1"]: ("DOWN", "fp"),
	KEYIDS["KEY_0"]: ("0",),
	KEYIDS["KEY_1"]: ("1",),
	KEYIDS["KEY_2"]: ("2",),
	KEYIDS["KEY_3"]: ("3",),
	KEYIDS["KEY_4"]: ("4",),
	KEYIDS["KEY_5"]: ("5",),
	KEYIDS["KEY_6"]: ("6",),
	KEYIDS["KEY_7"]: ("7",),
	KEYIDS["KEY_8"]: ("8",),
	KEYIDS["KEY_9"]: ("9",),
	KEYIDS["KEY_AUDIO"]: ("YELLOW",),
	KEYIDS["KEY_BLUE"]: ("BLUE",),
	KEYIDS["KEY_BOOKMARKS"]: ("PLUGIN",),
	KEYIDS["KEY_CHANNELDOWN"]: ("BOUQUET-",),
	KEYIDS["KEY_CHANNELUP"]: ("BOUQUET+",),
	KEYIDS["KEY_DOWN"]: ("DOWN",),
	KEYIDS["KEY_EDIT"]: ("EPGSETUP",),
	KEYIDS["KEY_EPG"]: ("EPG",),
	KEYIDS["KEY_EXIT"]: ("EXIT",),
	KEYIDS["KEY_FASTFORWARD"]: ("FORWARD",),
	KEYIDS["KEY_FAVORITES"]: ("FAV",),
	KEYIDS["KEY_GREEN"]: ("GREEN",),
	KEYIDS["KEY_HELP"]: ("HELP",),
	KEYIDS["KEY_INFO"]: ("INFO",),
	KEYIDS["KEY_LAST"]: ("BACK",),
	KEYIDS["KEY_LEFT"]: ("LEFT",),
	KEYIDS["KEY_MEDIA"]: ("MEDIA",),
	KEYIDS["KEY_MENU"]: ("MENU",),
	KEYIDS["KEY_MUTE"]: ("MUTE",),
	KEYIDS["KEY_NEXT"]: ("ARROWRIGHT",),
	KEYIDS["KEY_NEXTSONG"]: ("NEXTSONG",),
	KEYIDS["KEY_OK"]: ("OK",),
	KEYIDS["KEY_PLAY"]: ("PLAY",),
	KEYIDS["KEY_PLAYPAUSE"]: ("PLAYPAUSE",),
	KEYIDS["KEY_POWER"]: ("POWER",),
	KEYIDS["KEY_PREVIOUS"]: ("ARROWLEFT",),
	KEYIDS["KEY_PREVIOUSSONG"]: ("PREVIOUSSONG",),
	KEYIDS["KEY_PROGRAM"]: ("TIMER",),
	KEYIDS["KEY_RADIO"]: ("RADIO",),
	KEYIDS["KEY_RECORD"]: ("RECORD",),
	KEYIDS["KEY_RED"]: ("RED",),
	KEYIDS["KEY_RIGHT"]: ("RIGHT",),
	KEYIDS["KEY_SCREEN"]: ("SCREEN",),
	KEYIDS["KEY_SEARCH"]: ("WWW",),
	KEYIDS["KEY_SLEEP"]: ("SLEEP",),
	KEYIDS["KEY_STOP"]: ("STOP",),
	KEYIDS["KEY_SUBTITLE"]: ("SUBTITLE",),
	KEYIDS["KEY_TEXT"]: ("TEXT",),
	KEYIDS["KEY_TV"]: ("TV",),
	KEYIDS["KEY_UP"]: ("UP",),
	KEYIDS["KEY_VIDEO"]: ("PVR",),
	KEYIDS["KEY_VOLUMEDOWN"]: ("VOL-",),
	KEYIDS["KEY_VOLUMEUP"]: ("VOL+",),
	KEYIDS["KEY_YELLOW"]: ("YELLOW",)
}, {  # id=1 - dmm0 remote directory, other than DM8000.
	# However, the dmm0 rcpositions.xml file should define
	# an <rc id=1 /> element, but it does not, it only has
	# an <rc id=2 /> element.
	#
	# The rcpositions.xml file defines <button/> elements,
	# but they do not appear to emit codes.
	KEYIDS["BTN_0"]: ("UP", "fp"),
	KEYIDS["BTN_1"]: ("DOWN", "fp"),
	KEYIDS["KEY_0"]: ("0",),
	KEYIDS["KEY_1"]: ("1",),
	KEYIDS["KEY_2"]: ("2",),
	KEYIDS["KEY_3"]: ("3",),
	KEYIDS["KEY_4"]: ("4",),
	KEYIDS["KEY_5"]: ("5",),
	KEYIDS["KEY_6"]: ("6",),
	KEYIDS["KEY_7"]: ("7",),
	KEYIDS["KEY_8"]: ("8",),
	KEYIDS["KEY_9"]: ("9",),
	KEYIDS["KEY_AUDIO"]: ("AUDIO",),
	KEYIDS["KEY_BLUE"]: ("BLUE",),
	KEYIDS["KEY_BOOKMARKS"]: ("PLUGIN",),
	KEYIDS["KEY_CHANNELDOWN"]: ("BOUQUET-",),
	KEYIDS["KEY_CHANNELUP"]: ("BOUQUET+",),
	KEYIDS["KEY_DOWN"]: ("DOWN",),
	KEYIDS["KEY_EDIT"]: ("EPGSETUP",),
	KEYIDS["KEY_EPG"]: ("EPG",),
	KEYIDS["KEY_EXIT"]: ("EXIT",),
	KEYIDS["KEY_FASTFORWARD"]: ("BLUE", "SHIFT"),
	KEYIDS["KEY_FAVORITES"]: ("FAV",),
	KEYIDS["KEY_GREEN"]: ("GREEN",),
	KEYIDS["KEY_HELP"]: ("HELP",),
	KEYIDS["KEY_INFO"]: ("INFO",),
	KEYIDS["KEY_LAST"]: ("BACK",),
	KEYIDS["KEY_LEFT"]: ("LEFT",),
	KEYIDS["KEY_MEDIA"]: ("MEDIA",),
	KEYIDS["KEY_MENU"]: ("MENU",),
	KEYIDS["KEY_MUTE"]: ("MUTE",),
	KEYIDS["KEY_NEXT"]: ("ARROWRIGHT",),
	KEYIDS["KEY_OK"]: ("OK",),
	KEYIDS["KEY_PLAY"]: ("GREEN", "SHIFT"),
	KEYIDS["KEY_PAUSE"]: ("YELLOW", "SHIFT"),
	KEYIDS["KEY_POWER"]: ("POWER",),
	KEYIDS["KEY_PREVIOUS"]: ("ARROWLEFT",),
	KEYIDS["KEY_PROGRAM"]: ("TIMER",),
	KEYIDS["KEY_RADIO"]: ("RADIO",),
	KEYIDS["KEY_RECORD"]: ("RADIO", "SHIFT"),
	KEYIDS["KEY_RED"]: ("RED",),
	KEYIDS["KEY_REWIND"]: ("RED", "SHIFT"),
	KEYIDS["KEY_RIGHT"]: ("RIGHT",),
	KEYIDS["KEY_SCREEN"]: ("SCREEN",),
	KEYIDS["KEY_SEARCH"]: ("WWW",),
	KEYIDS["KEY_SLEEP"]: ("SLEEP",),
	KEYIDS["KEY_STOP"]: ("TV", "SHIFT"),
	KEYIDS["KEY_SUBTITLE"]: ("SUBTITLE",),
	KEYIDS["KEY_TEXT"]: ("TEXT",),
	KEYIDS["KEY_TV"]: ("TV",),
	KEYIDS["KEY_UP"]: ("UP",),
	KEYIDS["KEY_VIDEO"]: ("PVR",),
	KEYIDS["KEY_VOLUMEDOWN"]: ("VOL-",),
	KEYIDS["KEY_VOLUMEUP"]: ("VOL+",),
	KEYIDS["KEY_YELLOW"]: ("YELLOW",)
}, {  # id=2 - Everything else.
	KEYIDS["BTN_0"]: ("UP", "fp"),
	KEYIDS["BTN_1"]: ("DOWN", "fp"),
	KEYIDS["KEY_0"]: ("0",),
	KEYIDS["KEY_1"]: ("1",),
	KEYIDS["KEY_2"]: ("2",),
	KEYIDS["KEY_3"]: ("3",),
	KEYIDS["KEY_4"]: ("4",),
	KEYIDS["KEY_5"]: ("5",),
	KEYIDS["KEY_6"]: ("6",),
	KEYIDS["KEY_7"]: ("7",),
	KEYIDS["KEY_8"]: ("8",),
	KEYIDS["KEY_9"]: ("9",),
	KEYIDS["KEY_ARCHIVE"]: ("HISTORY",),
	KEYIDS["KEY_AUDIO"]: ("AUDIO",),
	KEYIDS["KEY_AUX"]: ("WIZTV",),
	KEYIDS["KEY_BACK"]: ("RECALL",),
	KEYIDS["KEY_BLUE"]: ("BLUE",),
	KEYIDS["KEY_BOOKMARKS"]: ("PLUGIN",),
	KEYIDS["KEY_CALENDAR"]: ("AUTOTIMER",),
	KEYIDS["KEY_CHANNELDOWN"]: ("BOUQUET-",),
	KEYIDS["KEY_CHANNELUP"]: ("BOUQUET+",),
	KEYIDS["KEY_CONTEXT_MENU"]: ("CONTEXT",),
	KEYIDS["KEY_DOWN"]: ("DOWN",),
	KEYIDS["KEY_EJECTCD"]: ("EJECTCD",),
	KEYIDS["KEY_END"]: ("END",),
	KEYIDS["KEY_ENTER"]: ("ENTER", "kbd"),
	KEYIDS["KEY_EPG"]: ("EPG",),
	KEYIDS["KEY_EXIT"]: ("EXIT",),
	KEYIDS["KEY_F1"]: ("F1",),
	KEYIDS["KEY_F2"]: ("F2",),
	KEYIDS["KEY_F3"]: ("F3",),
	KEYIDS["KEY_F4"]: ("F4",),
	KEYIDS["KEY_FASTFORWARD"]: ("FASTFORWARD",),
	KEYIDS["KEY_FAVORITES"]: ("FAV",),
	KEYIDS["KEY_FILE"]: ("LIST",),
	KEYIDS["KEY_GREEN"]: ("GREEN",),
	KEYIDS["KEY_GOTO"]: ("GOTO",),  # Missing.
	KEYIDS["KEY_HELP"]: ("HELP",),
	KEYIDS["KEY_HOME"]: ("HOME",),
	KEYIDS["KEY_HOMEPAGE"]: ("HOMEPAGE",),
	KEYIDS["KEY_INFO"]: ("INFO",),
	KEYIDS["KEY_KEYBOARD"]: ("KEYBOARD",),
	KEYIDS["KEY_LAST"]: ("BACK",),
	KEYIDS["KEY_LEFT"]: ("LEFT",),
	KEYIDS["KEY_LIST"]: ("PLAYLIST",),
	KEYIDS["KEY_MEDIA"]: ("MEDIA",),
	KEYIDS["KEY_MENU"]: ("MENU",),
	KEYIDS["KEY_MODE"]: ("VKEY",),
	KEYIDS["KEY_MUTE"]: ("MUTE",),
	KEYIDS["KEY_NEXT"]: ("ARROWRIGHT",),
	KEYIDS["KEY_NEXTSONG"]: ("NEXTSONG",),
	KEYIDS["KEY_OK"]: ("OK",),
	KEYIDS["KEY_OPTION"]: ("OPTION",),
	KEYIDS["KEY_PAGEDOWN"]: ("PAGEDOWN",),
	KEYIDS["KEY_PAGEUP"]: ("PAGEUP",),
	KEYIDS["KEY_PAUSE"]: ("PAUSE",),
	KEYIDS["KEY_PC"]: ("LAN",),
	KEYIDS["KEY_PLAY"]: ("PLAY",),
	KEYIDS["KEY_PLAYPAUSE"]: ("PLAYPAUSE",),
	KEYIDS["KEY_POWER"]: ("POWER",),
	KEYIDS["KEY_PREVIOUS"]: ("ARROWLEFT",),
	KEYIDS["KEY_PREVIOUSSONG"]: ("PREVIOUSSONG",),
	KEYIDS["KEY_PROGRAM"]: ("TIMER",),
	KEYIDS["KEY_PVR"]: ("PVR",),
	KEYIDS["KEY_QUESTION"]: ("ABOUT",),
	KEYIDS["KEY_RADIO"]: ("RADIO",),
	KEYIDS["KEY_RECORD"]: ("RECORD",),
	KEYIDS["KEY_RED"]: ("RED",),
	KEYIDS["KEY_REWIND"]: ("REWIND",),
	KEYIDS["KEY_RIGHT"]: ("RIGHT",),
	KEYIDS["KEY_SAT"]: ("SAT",),
	KEYIDS["KEY_SCREEN"]: ("SCREEN",),
	KEYIDS["KEY_SEARCH"]: ("WWW",),
	KEYIDS["KEY_SETUP"]: ("SETUP",),
	KEYIDS["KEY_SLEEP"]: ("SLEEP",),
	KEYIDS["KEY_SLOW"]: ("SLOW",),
	KEYIDS["KEY_STOP"]: ("STOP",),
	KEYIDS["KEY_SUBTITLE"]: ("SUBTITLE",),
	KEYIDS["KEY_SWITCHVIDEOMODE"]: ("VMODE",),
	KEYIDS["KEY_TEXT"]: ("TEXT",),
	KEYIDS["KEY_TIME"]: ("TIMESHIFT",),
	KEYIDS["KEY_TV"]: ("TV",),
	KEYIDS["KEY_UP"]: ("UP",),
	KEYIDS["KEY_VIDEO"]: ("VIDEO",),
	# KEYIDS["KEY_VMODE"]: ("VMODE",),  # This value is deprecated use KEY_SWITCHVIDEOMODE instead.
	KEYIDS["KEY_VOLUMEDOWN"]: ("VOL-",),
	KEYIDS["KEY_VOLUMEUP"]: ("VOL+",),
	KEYIDS["KEY_YELLOW"]: ("YELLOW",),
	KEYIDS["KEY_ZOOM"]: ("ZOOM",),
	# Discrete power codes
	KEYIDS["KEY_POWER2"]: ("POWER2",),
	KEYIDS["KEY_SUSPEND"]: ("SUSPEND",),
	KEYIDS["KEY_WAKEUP"]: ("WAKEUP",),
	# Placeholder definition to assist with remote control updates.
	KEYIDS["KEY_RESERVED"]: ("UNKNOWN",)

}, {  # id=3 - XP1000.
	# The xp1000/rcpositions file defines PLAY and PAUSE
	# at the same location where it should just define
	# PLAYPAUSE there. It has similar overlayed incorrect
	# definitions for play & pause rather than play/pause
	# in remote.html.
	KEYIDS["BTN_0"]: ("UP", "fp"),
	KEYIDS["BTN_1"]: ("DOWN", "fp"),
	KEYIDS["KEY_0"]: ("0",),
	KEYIDS["KEY_1"]: ("1",),
	KEYIDS["KEY_2"]: ("2",),
	KEYIDS["KEY_3"]: ("3",),
	KEYIDS["KEY_4"]: ("4",),
	KEYIDS["KEY_5"]: ("5",),
	KEYIDS["KEY_6"]: ("6",),
	KEYIDS["KEY_7"]: ("7",),
	KEYIDS["KEY_8"]: ("8",),
	KEYIDS["KEY_9"]: ("9",),
	KEYIDS["KEY_AUDIO"]: ("AUDIO",),
	KEYIDS["KEY_BLUE"]: ("BLUE",),
	KEYIDS["KEY_BOOKMARKS"]: ("PORTAL",),
	KEYIDS["KEY_CHANNELDOWN"]: ("BOUQUET-",),
	KEYIDS["KEY_CHANNELUP"]: ("BOUQUET+",),
	KEYIDS["KEY_DOWN"]: ("DOWN",),
	KEYIDS["KEY_EPG"]: ("EPG",),
	KEYIDS["KEY_EXIT"]: ("EXIT",),
	KEYIDS["KEY_FASTFORWARD"]: ("FASTFORWARD",),
	KEYIDS["KEY_GREEN"]: ("GREEN",),
	KEYIDS["KEY_HELP"]: ("HELP",),
	KEYIDS["KEY_INFO"]: ("INFO",),
	KEYIDS["KEY_LEFT"]: ("LEFT",),
	KEYIDS["KEY_MENU"]: ("MENU",),
	KEYIDS["KEY_MUTE"]: ("MUTE",),
	KEYIDS["KEY_NEXT"]: ("ARROWRIGHT",),
	KEYIDS["KEY_NEXTSONG"]: ("NEXTSONG",),
	KEYIDS["KEY_OK"]: ("OK",),
	KEYIDS["KEY_PLAY"]: ("PLAY",),
	KEYIDS["KEY_PLAYPAUSE"]: ("PLAYPAUSE",),
	KEYIDS["KEY_POWER"]: ("POWER",),
	KEYIDS["KEY_PREVIOUS"]: ("ARROWLEFT",),
	KEYIDS["KEY_PREVIOUSSONG"]: ("PREVIOUSSONG",),
	KEYIDS["KEY_PROGRAM"]: ("TIMER",),
	KEYIDS["KEY_RADIO"]: ("RADIO",),
	KEYIDS["KEY_RECORD"]: ("RECORD",),
	KEYIDS["KEY_RED"]: ("RED",),
	KEYIDS["KEY_REWIND"]: ("REWIND",),
	KEYIDS["KEY_RIGHT"]: ("RIGHT",),
	KEYIDS["KEY_SLEEP"]: ("SLEEP",),
	KEYIDS["KEY_STOP"]: ("STOP",),
	KEYIDS["KEY_SUBTITLE"]: ("SUBTITLE",),
	KEYIDS["KEY_SWITCHVIDEOMODE"]: ("VMODE",),
	KEYIDS["KEY_TEXT"]: ("TEXT",),
	KEYIDS["KEY_TV"]: ("TV",),
	KEYIDS["KEY_UP"]: ("UP",),
	KEYIDS["KEY_VIDEO"]: ("PVR",),
	# KEYIDS["KEY_VMODE"]: ("VMODE",),  # This value is deprecated use KEY_SWITCHVIDEOMODE instead.
	KEYIDS["KEY_VOLUMEDOWN"]: ("VOL-",),
	KEYIDS["KEY_VOLUMEUP"]: ("VOL+",),
	KEYIDS["KEY_YELLOW"]: ("YELLOW",)
}, {  # id=4 - Formuler F1/F3.
	# The formuler1 rcpositions file seems to define
	# the FF and REW keys as FASTFORWARD and KEY_REWIND,
	# but the remote.xml file issues KEY_PREVIOUSSONG
	# and KEY_NEXTSONG.
	KEYIDS["BTN_0"]: ("UP", "fp"),
	KEYIDS["BTN_1"]: ("DOWN", "fp"),
	KEYIDS["KEY_0"]: ("0",),
	KEYIDS["KEY_1"]: ("1",),
	KEYIDS["KEY_2"]: ("2",),
	KEYIDS["KEY_3"]: ("3",),
	KEYIDS["KEY_4"]: ("4",),
	KEYIDS["KEY_5"]: ("5",),
	KEYIDS["KEY_6"]: ("6",),
	KEYIDS["KEY_7"]: ("7",),
	KEYIDS["KEY_8"]: ("8",),
	KEYIDS["KEY_9"]: ("9",),
	KEYIDS["KEY_AUDIO"]: ("AUDIO",),
	KEYIDS["KEY_BACK"]: ("RECALL",),
	KEYIDS["KEY_BLUE"]: ("BLUE",),
	KEYIDS["KEY_BOOKMARKS"]: ("PLAYLIST",),
	KEYIDS["KEY_CHANNELDOWN"]: ("BOUQUET-",),
	KEYIDS["KEY_CHANNELUP"]: ("BOUQUET+",),
	KEYIDS["KEY_CONTEXT_MENU"]: ("CONTEXT",),
	KEYIDS["KEY_DOWN"]: ("DOWN",),
	KEYIDS["KEY_EPG"]: ("EPG",),
	KEYIDS["KEY_EXIT"]: ("EXIT",),
	KEYIDS["KEY_F1"]: ("F1",),
	KEYIDS["KEY_F2"]: ("F2",),
	KEYIDS["KEY_F3"]: ("F3",),
	KEYIDS["KEY_FASTFORWARD"]: ("FASTFORWARD",),
	KEYIDS["KEY_FAVORITES"]: ("FAVORITES",),
	KEYIDS["KEY_GREEN"]: ("GREEN",),
	KEYIDS["KEY_HELP"]: ("HELP",),
	KEYIDS["KEY_INFO"]: ("INFO",),
	KEYIDS["KEY_LEFT"]: ("LEFT",),
	KEYIDS["KEY_MENU"]: ("MENU",),
	KEYIDS["KEY_MUTE"]: ("MUTE",),
	KEYIDS["KEY_NEXT"]: ("ARROWRIGHT",),
	KEYIDS["KEY_OK"]: ("OK",),
	KEYIDS["KEY_PAUSE"]: ("PAUSE",),
	KEYIDS["KEY_PLAY"]: ("PLAY",),
	KEYIDS["KEY_POWER"]: ("POWER",),
	KEYIDS["KEY_PREVIOUS"]: ("ARROWLEFT",),
	KEYIDS["KEY_RADIO"]: ("RADIO",),
	KEYIDS["KEY_RECORD"]: ("RECORD",),
	KEYIDS["KEY_RED"]: ("RED",),
	KEYIDS["KEY_REWIND"]: ("REWIND",),
	KEYIDS["KEY_RIGHT"]: ("RIGHT",),
	KEYIDS["KEY_STOP"]: ("STOP",),
	KEYIDS["KEY_TEXT"]: ("TEXT",),
	KEYIDS["KEY_TV"]: ("TV",),
	KEYIDS["KEY_UP"]: ("UP",),
	KEYIDS["KEY_VIDEO"]: ("PVR",),
	KEYIDS["KEY_VOLUMEDOWN"]: ("VOL-",),
	KEYIDS["KEY_VOLUMEUP"]: ("VOL+",),
	KEYIDS["KEY_YELLOW"]: ("YELLOW",)
}]

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
			try:
				for keyId, names in KEYDESCRIPTIONS[index].items():
					if names[0] == name:
						break
			except:
				pass
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
	if rcButtons:
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
def buildXML(filename, buttonList, rcButtons):
	xml = []
	xml.append("<rcs>")
	if rcButtons:
		id = rcButtons.get("id", 2)
		image = rcButtons.get("image")
	if image:
		xml.append("\t<rc image=\"%s\">" % image)
	else:
		xml.append("\t<rc image=\"%s\">" % "\t<rc>")
	for button in buttonList:
		attribs = []
		id = rcButtons[button].get("id", "KEY_RESERVED")
		keyId = rcButtons[button].get("keyId", 0)
		remap = rcButtons[button].get("remap")
		if remap:
			attribs.append("id=\"%s\"" % remap)
			attribs.append("remap=\"%s\"" % id)
		else:
			attribs.append("id=\"%s\"" % id)
		attribs.append("label=\"%s\"" % rcButtons[button].get("label", ""))
		attribs.append("pos=\"%s\"" % ",".join([str(x) for x in rcButtons[button].get("pos", "")]))
		title = rcButtons[button].get("title", "")
		shape = rcButtons[button].get("shape", "")
		coords = rcButtons[button].get("coords", "")
		if title and shape and coords:
			attribs.append("title=\"%s\"" % title)
			attribs.append("shape=\"%s\"" % shape)
			attribs.append("coords=\"%s\"" % ",".join([str(x) for x in coords]))
		xml.append("\t\t<button %s />" % " ".join(attribs))
	xml.append("\t</rc>")
	xml.append("</rcs>")
	if rcButtons:
		logMessage(LOG_REPORT, "%d buttons loaded, %d buttons verified and written to the XML file." % (len(rcButtons.get("buttons")), len(buttonList)))
	saveFile(filename, xml)
	return


def saveFile(filename, content):
	filename = "%s-new" % filename
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
	if rcButtons:
		buildXML(filename, buttonList, rcButtons)
logMessage(LOG_PROGRAM, "\nProcessing complete.")
exit(0)
