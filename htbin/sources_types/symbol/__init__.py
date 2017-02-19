"""
Callable or data library symbol
"""

import cgi
import lib_uris
import lib_util
import lib_common
from lib_properties import pc

def EntityOntology():
	return ( ["Name","File"], )

def EntityName(entity_ids_arr,entity_host):
	entity_id = entity_ids_arr[0]
	try:
		# Trailing padding.
		resu = lib_util.Base64Decode(entity_id)
		# TODO: LE FAIRE AUSSI POUR LES AUTRES SYMBOLES.
		resu = cgi.escape(resu)
		return resu
	except TypeError:
		exc = sys.exc_info()[1]
		sys.stderr.write("CANNOT DECODE: symbol=(%s):%s\n"%(entity_id,str(exc)))
		return entity_id


# Each entity can have such a file with its name as file name.
# Then in its file, by convention adds information to a node.
def AddInfo(grph,node,entity_ids_arr):
	# TODO: Define symbol with two different key/vals, instead of this. Bad syntax !!!
	symbole_name = entity_ids_arr[0]
	try:
		file = entity_ids_arr[1]
	except IndexError:
		file = ""

	# WRONG, TODO: Must check the node ???
	fileNode = lib_common.gUriGen.FileUri( file )
	grph.add( ( fileNode, pc.property_symbol_defined, node ) )

def AddFunctionCall( grph, callNodePrev, procNode, callName, fileName ):
	if callName != None:
		callNodeNew = lib_common.gUriGen.SymbolUri( callName, fileName )
		if not callNodePrev is None:
			# Intermediary function in the callstack.
			grph.add( ( callNodeNew, pc.property_calls, callNodePrev ) )
		nodeFile = lib_common.gUriGen.FileUri( fileName )
		grph.add( ( nodeFile, pc.property_defines, callNodeNew ) )
		return callNodeNew
	else:
		# Top-level function of the process.
		if not callNodePrev is None:
			grph.add( ( procNode, pc.property_calls, callNodePrev ) )
		return None
