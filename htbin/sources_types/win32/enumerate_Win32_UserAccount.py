#!/usr/bin/python

"""
Windows users
"""

import sys
import socket
import rdflib
import psutil
import lib_common
import lib_util
from lib_properties import pc

# Necessary otherwise it is displayed on Linux machines,
# as it does not import any Windows-specific module.
Usable = lib_util.UsableWindows

# Meme chose que enumerate.user.py mais ca permettra plus facilement de s'affranchir de psutil.

def Main():
	cgiEnv = lib_common.CgiEnv()

	grph = rdflib.Graph()

	# [suser(name='Remi', terminal=None, host='0.246.33.0', started=1411052436.0)]

	try:
		# Windows XP, Python 3.
		try:
			# Windows XP, Python 3.4.
			users_list = psutil.users()
		except AttributeError:
			# Linux and Python 2.5
			# Windows 7, Python 3.2 : mais c'est la version de psutil qui compte.
			users_list = psutil.get_users()
	except AttributeError:
		# AttributeError: 'module' object has no attribute 'users'
		lib_common.ErrorMessageHtml("Function users() not available")

	for user in users_list:
		usrNam = lib_common.FormatUser( user.name )
		userNode = lib_common.gUriGen.UserUri( usrNam )

		grph.add( ( lib_common.nodeMachine, pc.property_user, userNode ) )

	cgiEnv.OutCgiRdf(grph)

if __name__ == '__main__':
	Main()