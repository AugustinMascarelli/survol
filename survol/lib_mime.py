import os
import sys
import lib_util
import lib_common
from lib_properties import pc

try:
	import mimetypes
	mimelib_present = True
except ImportError:
	mimelib_present = False

def FilenameToMime(pathName):
	sys.stderr.write("FilenameToMime pathName=%s\n"%pathName)

	# On Linux, we want to read text files in the /proc filesystem
	if pathName.startswith("/proc/"):
		return ['text/plain', None]


	# Some types might not be well processed.
	fileName, fileExt = os.path.splitext(pathName)
	extUpper = fileExt.upper()

	if extUpper in [".LOG"]:
		return ['text/plain', None]

	if mimelib_present:
		# For example: ('text/plain', None)
		return mimetypes.guess_type( pathName )
	else:
		# Last chance if module is not available.
		# TODO: This can easily be completed.
		if extUpper in [".JPG",".JPEG"]:
			return ['image/jpeg', None]
		if extUpper in [".TXT"]:
			return ['image/jpeg', None]

		mime_stuff = [None]

# This encodes the Mime type in the mode associated to an Url.
# The CGI "mode" parameter can be for example:
# "svg"                 Must be displayed in SVG after conversion to DOT.
# "rdf"                 Displayed as an RDF document.
# "html"                Displayed into HTML.
# "json"                Into JSON, read by a D3 Javascript library.
# "menu"                Generates a hierarchical menu for Javascript.
# "edit"                Edition of the other CGI parametgers.
# "mime:text/plain"     Displayed as a Mime document.
# "mime:image:bmp"      Same ...
mimeModePrefix = "mime:"

def AddMimeUrl(grph,filNode, entity_type,mime_type,entity_id_arr):
	entity_host = None
	if entity_host:
		genObj = lib_common.RemoteBox(entity_host)
	else:
		genObj = lib_common.gUriGen

	mimeNode = genObj.UriMakeFromScript( '/entity_mime.py', entity_type, *entity_id_arr )

	# So that the MIME type is known without loading the URLs.
	# Also, it allows to force a specific MIME type.
	# The MIME type is not coded in the property because it is an attribute of the object.

	# mimeNodeWithMode =  lib_util.AnyUriModed(mimeNode, "mime/" + mime_type)
	# sys.stderr.write("lib_mime.AddMimeUrl BEFORE mimeNode=%s\n"%(mimeNode))
	mimeNodeWithMode = mimeNode + "&amp;amp;" + "mode=" + mimeModePrefix + mime_type

	grph.add( ( filNode, pc.property_rdf_data_nolist2, lib_common.NodeUrl(mimeNodeWithMode) ) )

# If the CGI parameter is for example: "...&mode=
def ModeToMimeType(urlMode):
	return urlMode[5:]

def GetMimeTypeFromUrl(url):
	urlMode = lib_util.GetModeFromUrl(url)
	if urlMode and urlMode.startswith(mimeModePrefix):
		return ModeToMimeType(urlMode)
	else:
		return ""

