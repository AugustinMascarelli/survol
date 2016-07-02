import os
import re
import sys
import rdflib
import socket
import base64
import importlib

# In Python 3, urllib.quote has been moved to urllib.parse.quote and it does handle unicode by default.
try:
	from urllib import quote,unquote
except ImportError:
	from urllib.parse import quote,unquote

################################################################################

def EncodeEntityId(entity_type,entity_id):
	return "xid=%s.%s" % ( entity_type, entity_id )

################################################################################

def HttpPrefix():

	# Default values for ease of testing, so CGI scripts can be run as is from command line..
	try:
		server_addr = os.environ['SERVER_NAME']

		# This is an attempt to fix a problem when running cgiserver.py:
		# * The URL is 127.0.0.1:8000/index.htm
		# * SERVER_NAME="rchateau-hp"
		# * REMOTE_HOST="rchateau-hp"
		# * Pinging rchateau-HP [fe80::3c7a:339:64f0:2161%11]
		try:
			remote_host = os.environ['REMOTE_HOST']
			if server_addr == remote_host:
				server_addr = "127.0.0.1"
		except KeyError:
			pass

	except KeyError:
		# Local use .
		server_addr = "127.0.0.1"
	
	try:
		server_port = os.environ['SERVER_PORT']
	except KeyError:
		# Should not happen.
		server_port = "8080"

	# BEWARE: Colons are forbidden in URIs apparently !!!
	# Due to a very strange bug which displays:
	# "http://127.0.0.1:80/PythonStyle/htbin/entity.py" ... 
	# does not look like a valid URI, trying to serialize this will break.
	# But if we do not add "http:" etc... SVG adds its prefix "127.0.0.1" etc...
	return 'http://' + server_addr + ':' + server_port


def UriRootHelper():
	try:
		# SCRIPT_NAME=/PythonStyle/htbin/internals/print.py
		scriptNam=os.environ['SCRIPT_NAME']
		idx = scriptNam.find('htbin')
		root = scriptNam[:idx] + 'htbin'

	except KeyError:
		# If this runs from the command line and not as a CGI script,
		# then this environment variable is not set.
		root = "/NotRunningAsCgi"
	return HttpPrefix() + root

uriRoot = UriRootHelper()

################################################################################
# Aucune idee pourquoi on fait ce traitement.
def HostName():
	socketGetHostNam = socket.gethostname()
	if socketGetHostNam.find('.')>=0:
		# 'rchateau-HP'
		name=socketGetHostNam
	else:
		# 'rchateau-HP.home'
		name=socket.gethostbyaddr(socketGetHostNam)[0]
	return name


# hostName
currentHostname = HostName()

# Attention car il pourrait y avor plusieurs adresses IP.
try:
	localIP = socket.gethostbyname(currentHostname)
except Exception:
	# Apparently, it happens if the router is down.
	localIP = "127.0.0.1"

def IsLocalAddress(anHostNam):
	# Maybe entity_host="http://192.168.1.83:5988"
	hostOnly = EntHostToIp(anHostNam)
	if hostOnly in [ None, "", "localhost", "127.0.0.1", currentHostname ]:
		return True

	try:
		ipOnly = socket.gethostbyname(hostOnly)
	# socket.gaierror
	except Exception:
		# Unknown machine
		exc = sys.exc_info()[1]
		sys.stderr.write("IsLocalAddress anHostNam=%s:%s\n" % ( anHostNam, str(exc) ) )
		return False

	if ipOnly in [ "0.0.0.0", "127.0.0.1", localIP ]:
		return True

	return False

# Beware: lib_util.currentHostname="Unknown-30-b5-c2-02-0c-b5-2.home"
# socket.gethostname() = 'Unknown-30-b5-c2-02-0c-b5-2.home'
# socket.gethostbyaddr(hst) = ('Unknown-30-b5-c2-02-0c-b5-2.home', [], ['192.168.1.88'])
def SameHostOrLocal( srv, entHost ):
	if ( entHost == srv ) or ( ( entHost is None or entHost in ["","0.0.0.0"] ) and ( localIP == srv ) ) or ( entHost == "*"):
		# We might add credentials.
		# sys.stderr.write("SameHostOrLocal entHost=%s localIP=%s srv=%s SAME\n" % ( entHost, localIP, srv ) )
		return True
	else:
		# sys.stderr.write("SameHostOrLocal entHost=%s localIP=%s srv=%s Different\n" % ( entHost, localIP, srv ) )
		return False

################################################################################


# TODO: SUPPRIMER LA REFERENCE ABSOLUE !!!!!!!

def TopUrl( entityType, entityId ):
	if re.match( ".*/htbin/entity.py.*", os.environ['SCRIPT_NAME'] ):
		if entityType == "":
			topUrl = uriRoot + "/../index.htm"
		else:
			# Same as in objtypes.py
			# if entityId in ("","Id=") or entity.endswith("="):
			# Not reliable: What does it mean to have "Id=" or "Name=" ?
			if entityId == "" or re.match( "[a-zA-Z_]*=", entityId ):
				topUrl = uriRoot + "/entity.py"
			else:
				topUrl = EntityUri( entityType, "" )
	else:
		topUrl = uriRoot + "/entity.py"
	return topUrl

################################################################################

# This, because graphviz transforms a "\L" (backslash-L) into "<TABLE>". Example:
# http://127.0.0.1/PythonStyle/htbin/entity.py?xid=com_type_lib:C%3A%5CWINDOWS%5Csystem32%5CLangWrbk.dll
# Or if the url contains a file in "App\Local"
def EncodeUri(anStr):
	# sys.stderr.write("EncodeUri str=%s\n" % str(anStr) )

	strTABLE = anStr.replace("\\L","\\\\L")



	# In Python 3, urllib.quote has been moved to urllib.parse.quote and it does handle unicode by default.
	if sys.version_info >= (3,):


		# NORMALLEMENT CA DEVRAIT ETRE FAIT !!!
		###strTABLE = strTABLE.replace("&",";;;")



		return quote(strTABLE,'')
	else:

		# NORMALLEMENT CA DEVRAIT ETRE FAIT !!!
		###strTABLE = strTABLE.replace("&","%26")
		# UnicodeDecodeError: 'ascii' codec can't decode byte 0xe9 in position 32
		# strTABLE = unicode( strTABLE, 'utf-8')
		return quote(strTABLE,'ascii')

################################################################################

def RequestUri():
	try:
		script = os.environ["REQUEST_URI"]
	except:
		# Maybe this is started from a minimal http server.
		# "/htbin/entity.py"
		scriptName = os.environ['SCRIPT_NAME'] 
		# "xid=EURO%5CLONL00111310@process:16580"
		queryString = os.environ['QUERY_STRING'] 
		script = scriptName + "?" + queryString
	return script

################################################################################


# Apparently getcwd() changes during execution, or at least is not stable.
# "C:\\Users\\rchateau\\Developpement\\ReverseEngineeringApps\\PythonStyle\\htbin\\sources_top"
# SCRIPT_FILENAME=C:/Users/rchateau/Developpement/ReverseEngineeringApps/PythonStyle/htbin/internals/print.py
# REQUEST_URI=/Survol/htbin/internals/print.py
# SCRIPT_NAME=/Survol/htbin/internals/print.py
# getcwd=C:\Users\rchateau\Developpement\ReverseEngineeringApps\PythonStyle\htbin\internals
def TopScriptsFunc():
	# TODO: Use __file__ which might be faster ??
	currDir = os.getcwd()

	# TODO: WHY IS IT DISPLAYED TWICE ???? CIRCULAR IMPORT ??
	sys.stderr.write("TopScriptsFunc currDir=%s\n"%currDir)
	sys.stderr.write("TopScriptsFunc __file__=%s\n"%__file__)

	idx = currDir.find("htbin")
	# Maybe not running i Apache but in http.server (Python 3) or SimpleHttpServer (Python 2)
	if idx == -1:
		return currDir + "//htbin"
	else:
		return currDir[ : idx + 5 ]

gblTopScripts = TopScriptsFunc()

# TODO: This is necessary because now we import modules from htbin.
# TODO: We will also add htbin/revlib so it will not be necessary to set PYTHONPATH in Apache httpd.conf.
sys.path.append(gblTopScripts)
sys.stderr.write("sys.path=%s\n"%str(sys.path))
################################################################################

# Depending on the category, entity_host can have several forms.
# The name is misleading because it returns a host name,
# Which might or might not be an IP.
# TODO: Must be very fast !
def EntHostToIp(entity_host):
	# WBEM: http://192.168.1.88:5988
	#       https://jdd:test@acme.com:5959
	#       http://192.168.1.88:5988
	# TODO: Not sure this will work with IPV6
	mtch_host_wbem = re.match( "https?://([^/:]*).*", entity_host )
	if mtch_host_wbem:
		#sys.stderr.write("EntHostToIp WBEM=%s\n" % mtch_host_wbem.group(1) )
		return mtch_host_wbem.group(1)

	# WMI : \\RCHATEAU-HP
	mtch_host_wmi = re.match( r"\\\\([-0-9A-Za-z_\.]*)", entity_host )
	if mtch_host_wmi:
		#sys.stderr.write("EntHostToIp WBEM=%s\n" % mtch_host_wmi.group(1) )
		return mtch_host_wmi.group(1)

	# sys.stderr.write("EntHostToIp Custom=%s\n" % entity_host )
	return entity_host

# TODO: Coalesce with EntHostToIp
def EntHostToIpReally(entity_host):
	try:
		hostOnly = EntHostToIp(entity_host)
		return socket.gethostbyname(hostOnly)
	except Exception:
		return hostOnly

# BEWARE: This cannot work if the hostname contains a ":", see IPV6. MUST BE VERY FAST !!!
# TODO: Should also parse the namespace.
# TODO: Faudrait savoir, avec ou sans le prop=val ???
# ParseXid xid=CIM_ComputerSystem.Name=rchateau-HP
# ParseXid xid=CIM_ComputerSystem.Name=Unknown-30-b5-c2-02-0c-b5-2
def ParseXid(xid ):
	# sys.stderr.write( "ParseXid xid=%s\n" % (xid) )

	# First, we try to match our terminology.
	# The type can be in several directories separated by slashes: "oracle/table"
	# If suffixed with "/", it means namespaces.

	# A machine name can contain a domain name : "WORKGROUP\RCHATEAU-HP", the backslash cannot be at the beginning.
	# "WORKGROUP\RCHATEAU-HP@CIM_ComputerSystem.Name=Unknown-30-b5-c2-02-0c-b5-2"
	# "WORKGROUP\RCHATEAU-HP@oracle/table.Name=MY_TABLE"
	# BEWARE: This must NOT match "http://127.0.0.1:8000/htbin/namespaces_wbem.py?xid=http://192.168.1.83:5988/."
	# that is "http://192.168.1.83:5988/."
	# mtch_entity = re.match( r"([-0-9A-Za-z_]*\\?[-0-9A-Za-z_\.]*@)?([a-z0-9A-Z_/]*:?[a-z0-9A-Z_/]*)\.(.*)", xid )
	# Une classe commence par une lettre, pas de / consecutifs.
	# TODO: Filter when consecutives slashes.
	mtch_entity = re.match( r"([-0-9A-Za-z_]*\\?[-0-9A-Za-z_\.]*@)?([a-zA-Z_][a-z0-9A-Z_/]*)\.(.*)", xid )

	if mtch_entity:
		if mtch_entity.group(1) == None:
			entity_host = ""
		else:
			entity_host = mtch_entity.group(1)[:-1]

		entity_type = mtch_entity.group(2)
		entity_id_quoted = mtch_entity.group(3)

		entity_id = unquote(entity_id_quoted)

		return ( entity_type, entity_id, entity_host )

	# Apparently it is not a problem for the plain old entities.
	xid = unquote(xid)

	# WMI : \\RCHATEAU-HP\root\cimv2:Win32_Process.Handle="0"
	# Beware ! On Windows, namespaces are separated by backslashes.
	# WMI : \\RCHATEAU-HP\root\cimv2:Win32_Process.Handle="0"
	# http://127.0.0.1:8000/htbin/objtypes_wmi.py?xid=\\rchateau-HP\root\CIMV2\Applications%3A.
	# http://127.0.0.1:8000/htbin/class_wmi.py?xid=\\rchateau-HP\root\CIMV2%3AWin32_PerfFormattedData_Counters_IPHTTPSGlobal.
	# http://127.0.0.1:8000/htbin/entity_wmi.py?xid=\\RCHATEAU-HP\root\CIMV2%3AWin32_PerfFormattedData_Counters_IPHTTPSGlobal.Name%3D%22Default%22
	# TODO: BEWARE ! If the host name starts with a L, we have to "triplicate" the back-slash
	# TODO: otherwise graphviz replace "\L" par "<TABLE">
	mtch_ent_wmi = re.match( r"\\\\\\?([-0-9A-Za-z_\.]*)\\([^.]*)(\..*)", xid )
	if mtch_ent_wmi:
		grp = mtch_ent_wmi.groups()
		( entity_host, entity_type, entity_id_quoted ) = grp
		if entity_id_quoted is None:
			entity_id = ""
			# sys.stderr.write("WMI Class Cimom=%s ns_type=%s\n" % ( entity_host, entity_type ))
		else:
			entity_id = unquote(entity_id_quoted)[1:]
			# sys.stderr.write("WMI Object Cimom=%s ns_type=%s path=%s\n" % ( entity_host, entity_type, entity_id ))

		return ( entity_type, entity_id, entity_host )

	# WBEM: https://jdd:test@acme.com:5959/cimv2:Win32_SoftwareFeature.Name="Havana",ProductName="Havana",Version="1.0"
	#       http://192.168.1.88:5988/root/PG_Internal:PG_WBEMSLPTemplate
	#		"http://127.0.0.1:8000/htbin/namespaces_wbem.py?xid=http://192.168.1.83:5988/."
	#		"xid=http://192.168.1.88:5988/."
	mtch_ent_wbem = re.match( "(https?://[^/]*)/([^.]*)(\..*)?", xid )
	if mtch_ent_wbem:
		grp = mtch_ent_wbem.groups()
		( entity_host, entity_type, entity_id_quoted ) = grp
		# TODO: SAME LOGIC FOR THE TWO OTHER CASES !!!!!!!!!!!!!!
		if entity_id_quoted is None:
			entity_id = ""
			# sys.stderr.write("WBEM Class Cimom=%s ns_type=%s\n" % ( entity_host, entity_type ))
		else:
			entity_id = unquote(entity_id_quoted)[1:]
			# sys.stderr.write("WBEM Object Cimom=%s ns_type=%s path=%s\n" % ( entity_host, entity_type, entity_id ))

		return ( entity_type, entity_id, entity_host )

	# sys.stderr.write( "ParseXid=%s RETURNS NOTHING\n" % (xid) )
	return ( "", "", "" )

# TODO: Would probably be faster by searching for the last "/".
# MUST BE VERY FAST.
# '\\\\RCHATEAU-HP\\root\\cimv2:Win32_Process.Handle="0"'  => "root\\cimv2:Win32_Process"
# https://jdd:test@acme.com:5959/cimv2:Win32_SoftwareFeature.Name="Havana",ProductName="Havana",Version="1.0"  => ""
def ParseNamespaceType(ns_entity_type):
	# sys.stderr.write("ParseEntityType entity_type=%s\n" % ns_entity_type )
	nsSplit = ns_entity_type.split(":")
	if len(nsSplit) == 1:
		entity_namespace = ""
		entity_type = nsSplit[0]
	else:
		entity_namespace = nsSplit[0]
		entity_type = nsSplit[1]
	return ( entity_namespace, entity_type, ns_entity_type )


################################################################################

# A bit temporary.
def ScriptizeCimom(path, entity_type, cimom):
	return uriRoot + path + "?" + EncodeEntityId(cimom + "/" + entity_type,"")

# Properly encodes type and id into a URL.
# TODO: Ca va etre un peu un obstacle car ca code vraiment le type d'URL.
# Ne pas utiliser ca pour les Entity.
def Scriptize(path, entity_type, entity_id):
	return uriRoot + path + "?" + EncodeEntityId(entity_type,entity_id)

################################################################################

def EntityClassNode(entity_type, entity_namespace = "", entity_host = "", category = ""):
	if entity_type is None:
		entity_type = ""

	# WBEM: https://jdd:test@acme.com:5959/cimv2:Win32_SoftwareFeature.Name="Havana",ProductName="Havana",Version="1.0"
	if category == "WBEM":
		monikerClass = entity_host + "/" + entity_namespace + ":" + entity_type + "."
	# WMI : \\RCHATEAU-HP\root\cimv2:Win32_Process.Handle="0"
	elif category == "WMI":
		monikerClass = "\\\\" + entity_host + "\\" + entity_namespace + ":" + entity_type + "."
	# This is temporary.
	else:
		# En fait, on devrait pouvoir simplifier le format, comme avant, si pas de namespace ni de host: "type."
		monikerClass = ""
		if entity_host:
			monikerClass += entity_host + "@"
		# Should not happen.
		if entity_namespace:
			monikerClass += entity_namespace + "/:"
		monikerClass += entity_type + "."

	# TODO: Voir aussi EntityUrlFromMoniker.

	url = uriRoot + "/class_type_all.py?xid=" + EncodeUri(monikerClass)

	# sys.stdout.write("EntityClassUrl url=%s\n" % url)
	return rdflib.term.URIRef( url )
	# return url

################################################################################
# TODO: What about the namespace ?

def EntityUriFromDict(entity_type,entity_ids_kvp):
	entity_id = ",".join( "%s=%s" % ( pairKW, entity_ids_kvp[pairKW] ) for pairKW in entity_ids_kvp )

	url = Scriptize("/entity.py", entity_type, entity_id )
	return rdflib.term.URIRef( url )

# This is the most common case. Shame we call the slower function.
def EntityUri(entity_type,*entity_ids):
	return EntityUriDupl( entity_type, *entity_ids )

def EntityUriDupl(entity_type,*entity_ids,**extra_args):
	# sys.stderr.write("EntityUriDupl %s\n" % str(entity_ids))

	keys = OntologyClassKeys(entity_type)

	if len(keys) != len(entity_ids):
		sys.stderr.write("Different lens:%s and %s\n" % (str(keys),str(entity_ids))) 
	entity_id = ",".join( "%s=%s" % pairKW for pairKW in zip( keys, entity_ids ) )
	
	# Extra arguments, differentiating duplicates.
	entity_id += "".join( ",%s=%s" % ( extArg, extra_args[extArg] ) for extArg in extra_args )

	url = Scriptize("/entity.py", entity_type, entity_id )
	return rdflib.term.URIRef( url )

################################################################################

# Probably not necessary because we apparently always know
# if we need a WMI, WBEM or custom scripts. Not urgent to change this.
def EntityScriptFromPath(monikerEntity,is_class,is_namespace,is_hostname):
	if monikerEntity[0] == '\\':
		entIdx = 0
	elif monikerEntity[0:4] == 'http':
		entIdx = 1
	else:
		entIdx = 2

	if is_hostname:
		return ('namespaces_wmi.py','namespaces_wbem.py','entity.py')[ entIdx ]
	elif is_namespace:
		return ('objtypes_wmi.py','objtypes_wbem.py','objtypes.py')[ entIdx ]
	elif is_class:
		return ('class_wmi.py','class_wbem.py','class_type_all.py')[ entIdx ]
	else:
		return ('entity_wmi.py','entity_wbem.py','entity.py')[ entIdx ]

# Le parsing devra etre beaucoup plus performant.
# TODO: Creer trois fonctions un peu comme EntityClassUrl, car on connait toujorus la categorie.
def EntityUrlFromMoniker(monikerEntity,is_class=False,is_namespace=False,is_hostname=False):
	scriptPath = EntityScriptFromPath(monikerEntity,is_class,is_namespace,is_hostname)

	url = uriRoot + "/" + scriptPath + "?xid=" + EncodeUri(monikerEntity)
	return url

# Full natural path: We must try to merge it with WBEM Uris.
# '\\\\RCHATEAU-HP\\root\\cimv2:Win32_Process.Handle="0"'
# https://jdd:test@acme.com:5959/cimv2:Win32_SoftwareFeature.Name="Havana",ProductName="Havana",Version="1.0"

################################################################################

# Not really used at the moment.
CharTypesComposer = ","

# TODO: Find another solution more compatible with WBEM and WMI logic.
# Used to define subtypes.
def ComposeTypes(t1,t2):
	return t1 + CharTypesComposer + t2

################################################################################

# contentType = "text/rdf", "text/html", "image/svg+xml", "application/json" etc...
def HttpHeader( out_dest, contentType ):
	stri = "Content-Type: " + contentType + "\n\n"
	# Python 3.2
	try:
		out_dest.write( stri )
		return
	except TypeError:
		pass

	out_dest.write( stri.encode() )

################################################################################

def CopyFile( mime_type, fileName, outFd ):

	# read and write by chunks, so that it does not use all memory.
	filDes = open(fileName, 'rb')

	HttpHeader( outFd, mime_type )

	while True:
		chunk = filDes.read(1000000)
		if not chunk:
			break
		outFd.write( chunk )
	filDes.close()


################################################################################

# By the way, when calling a RDF source, we should check the type of the
# MIME document and if this is not RDF, the assumes it's an error 
# which must be displayed.
# This is used as a HTML page but also displayed in Javascript in a DIV block.
def InfoMessageHtml(message):
	HttpHeader( sys.stdout, "text/html")
	print("""
	<html>
	<head></head>
	""")
	print("<title>Error: Process=" + str(os.getpid()) + "</title>")
	
	print("<body>")

	print("<b>" + message + "</b><br>")

	# On Linux it says: "OSError: [Errno 2] No such file or directory"
	print('<table>')

	if sys.version_info >= (3,):
		print("<tr><td>Login</td><td>" + os.getlogin() + "</td></tr>")

	print("<tr><td>Cwd</td><td>" + os.getcwd() + "</td></tr>")
	print("<tr><td>OS</td><td>" + sys.platform + "</td></tr>")
	print("<tr><td>Version</td><td>" + sys.version + "</td></tr>")
	
	#print('<tr><td colspan="2"><b>Environment variables</b></td></tr>')
	#for key, value in os.environ.items():
	#	print("<tr><td>"+key+"</td><td>"+value+"</td></tr>")
	print('</table>')

	envsUrl = uriRoot + "/internals/print.py"
	print('Check <a href="' + envsUrl + '"">environment variables</a>.<br>')
	homeUrl = uriRoot + "/../index.htm"
	print('<a href="' + homeUrl + '"">Return home</a>.<br>')

	print("""
	</body></html>
	""")

################################################################################

# Returns the list of available object types: ["process", "file," group", etc...]
def ObjectTypesNoCache():
	# directory=C:\\Users\\rchateau\\Developpement\\ReverseEngineeringApps\\PythonStyle\\htbin\\sources_top/sources_types\r:
	directory = gblTopScripts + "/sources_types"
	sys.stderr.write("ObjectTypesNoCache directory="+directory+"\n")

	ld = len(directory)
	for path, dirs, files in os.walk(directory):
		if len(path) == ld:
			prefix = ""
		else:
			prefix = path[ld +1:].replace("\\","/") + "/"
		for dir in dirs:
			if dir != "__pycache__":
				yield prefix + dir

glbObjectTypes = None

# TODO: Should concatenate this to localOntology. Default value is "Id".
def ObjectTypes():
	global glbObjectTypes

	if glbObjectTypes is None:
		glbObjectTypes = set( ObjectTypesNoCache() )
		# sys.stderr.write("ObjectTypes glbObjectTypes="+str(glbObjectTypes)+"\n")

	return glbObjectTypes

################################################################################

isPlatformLinux = 'linux' in sys.platform
isPlatformWindows = 'win' in sys.platform

def UsableLinux(entity_type,entity_ids_arr):
	"""Runs on Linux only"""
	return isPlatformLinux

def UsableWindows(entity_type,entity_ids_arr):
	"""Runs on Windows only"""
	return isPlatformWindows

def UsableAsynchronousSource(entity_type,entity_ids_arr):
	"""Asychronous data source"""
	return False

# Tells if a file is executable code or library.
def UsableWindowsBinary(entity_type,entity_ids_arr):
	"""Windows executable or code file"""
	if not UsableWindows(entity_type,entity_ids_arr):
		return False
	fulFileName = entity_ids_arr[0]
	if os.path.isdir(fulFileName):
		return False
	filename, file_extension = os.path.splitext(fulFileName)
	# TODO: Must add library type for ELF and PE ?
	return file_extension.upper() in [".EXE", ".DLL", ".COM", ".OCX", ".SYS", ".ACM", ".BPL", ".DPL"]

# Applies for nm, dll, elftools.
def UsableLinuxBinary(entity_type,entity_ids_arr):
	"""Linux executable or code file"""
	if not UsableLinux(entity_type,entity_ids_arr):
		return False
	fulFileName = entity_ids_arr[0]
	if os.path.isdir(fulFileName):
		return False
	filename, file_extension = os.path.splitext(fulFileName)
	# TODO: Must add library type for ELF and PE ?
	if file_extension() in [".so", ".lib"]:
		return True
	# TODO: Finish this. Use "magic" module ??
	return True
	
	
################################################################################


# This overlaps DMTF and never contradicts it.
# BIENTOT ON N'EN AURA PROBABLEMENT PLUS BESOIN CAR ON VA UTILISER
# DES K-V PAIRS PARTOUT.
# ATTENTION A LA VIRGULE
localOntology = {
	"CIM_ComputerSystem"  : ( ["Name"], ),
	"CIM_Process"         : ( ["Handle"], ),
	"Win32_Service"       : ( ["Name"], ),
	"Win32_UserAccount"   : ( ["Name"], ),
	"class"               : ( ["Name","File"], ),
	"dbus/bus"            : ( ["Bus"], ),
	"dbus/connection"     : ( ["Bus","Connect"], ),
	"dbus/object"         : ( ["Bus","Connect","Obj"], ),
	"dbus/interface"      : ( ["Bus","Connect","Obj","Itf"], ),
	"odbc/dsn"            : ( ["Dsn"], ),
	"odbc/table"          : ( ["Dsn", "Table"], ),
	"odbc/column"         : ( ["Dsn", "Table", "Column"], ),
	"oracle/db"           : ( ["Db"], ),
	"oracle/package"      : ( ["Db","Schema","Package"], ),
	"oracle/package_body" : ( ["Db","Schema","Package"], ),
	"oracle/schema"       : ( ["Db","Schema"], ),
	"oracle/session"      : ( ["Db","Session"], ),
	"oracle/synonym"      : ( ["Db","Schema","Synonym"], ),
	"oracle/table"        : ( ["Db","Schema","Table"], ),
	"oracle/view"         : ( ["Db","Schema","View"], ),
	"sqlite/table"        : ( ["File","Table"], ),
	"sqlite/column"       : ( ["File","Table","Column"], ),
	"symbol"              : ( ["Name","File"], ),
}

# The key must match the DMTF standard. It might contain a namespace.
# TODO: Replace this by a single lookup in a single dict
# TODO: ... made of localOntology added to the directory of types.
def OntologyClassKeys(entity_type):
	try:
		# TODO: Temporarily until we do something more interesting, using the subtype.
		# entity_type = entity_type.split(CharTypesComposer)[0]

		# TODO: If cannot find it, load the associated module and retry.
		return localOntology[ entity_type ][0]
	except KeyError:
		pass

	# Et si on ne trouve pas chercher dans le module ?? lib_util.GetEntityModule(entity_type).GetFields()

	# If this class is in our ontology but has no defined properties.
	if entity_type in ObjectTypes():
		# Default single key for our specific classes.
		return [ "Id" ]

	# This could be replaced by a single lookup.
	return []

# Some classes exist on some platforms only.
# This applies locally only, otherwise the remote machine must be queried by some way.
def OntologyClassAvailable(entity_type):
	try:
		return localOntology[ entity_type ][1]
	except KeyError:
		return True
	except IndexError:
		return True

# Used for calling ArrayInfo. The order of arguments is strict.
def EntityIdToArray( entity_type, entity_id ):
	# sys.stderr.write("EntityIdToArray type=%s id=%s\n" % ( entity_type , entity_id ) )
	ontoKeys = OntologyClassKeys(entity_type)
	dictIds = SplitMoniker( entity_id )
	# sys.stderr.write("EntityIdToArray dictIds=%s\n" % ( str(dictIds) ) )
	# For the moment, this assumes that all keys are here.
	# Later, drop this constraint and allow WQL queries.
	return [ dictIds[ aKey ] for aKey in ontoKeys ]

################################################################################

# Used for example as the root in entity.py, obj_types.py and class_type_all.py.
# This is a bit articical but a root node is really needed here.
# It might contain &mode=svg or whatever, this should be removed.

def RootUri():
	callingUrl = RequestUri()
	# TODO: THIS IS A HACK. Here is the reason:
	# gui_create_svg_from_several_rdfs.py reads URL as RDF documents
	# and for this reason, it must appends "&mode=rdf" at the end of the URL.
	# So an ampersand is found in the SVG document, which is misprocessed.
	callingUrl = callingUrl.replace("&mode=rdf","")
	# TODO: We could also replace the ampersand by an HTML entity.
	# this might be necessary of there are useful CGI parameters to keep.
	callingUrl = callingUrl.replace("&","&amp;")
	return rdflib.term.URIRef(callingUrl)

################################################################################

# Concatenate key-value pairs to build the path of a WMI or WBEM moniker.
# TODO: SHOULD WE WRAP VALUES IN DOUBLE-QUOTES ?????
def BuildMonikerPath(dictKeyVal):
	return ','.join( [ '%s=%s' % ( wbemKey, dictKeyVal[wbemKey] ) for wbemKey in dictKeyVal ] )


# Slight modification from  http://stackoverflow.com/questions/16710076/python-split-a-string-respect-and-preserve-quotes
# 'Id=NT AUTHORITY\SYSTEM'         => ['Id=NT AUTHORITY\\SYSTEM']
# 'Id="NT =\\"AUTHORITY\SYSTEM"'   => ['Id=NT AUTHORITY\\SYSTEM']
def SplitMoniker(xid):
	# sys.stderr.write("SplitMoniker xid=%s\n" % xid )

	# spltLst = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', xid)
	spltLst = re.findall(r'(?:[^,"]|"(?:\\.|[^"])*")+', xid)

	# sys.stderr.write("SplitMoniker spltLst=%s\n" % ";".join(spltLst) )

	resu = dict()
	for spltWrd in spltLst:
		mtchEqualQuote = re.match(r'([A-Z0-9a-z_]+)="(.*)"', spltWrd)
		if mtchEqualQuote:
			# If there are quotes, they are dropped.
			resu[ mtchEqualQuote.group(1) ] = mtchEqualQuote.group(2)
		else:
			mtchEqualNoQuote = re.match(r'([A-Z0-9a-z_]+)=(.*)', spltWrd)
			if mtchEqualNoQuote:
				resu[ mtchEqualNoQuote.group(1) ] = mtchEqualNoQuote.group(2)

	# sys.stderr.write("SplitMoniker resu=%s\n" % str(resu) )

	return resu

# Builds a SQL query.
def SplitMonikToWQL(splitMonik,className):
	sys.stderr.write("splitMonik=[%s]\n" % str(splitMonik) )
	aQry = 'select * from %s ' % className
	qryDelim = "where"
	for qryKey in splitMonik:
		qryVal = splitMonik[qryKey]
		aQry += ' %s %s="%s"' % ( qryDelim, qryKey, qryVal )
		qryDelim = "and"

	sys.stderr.write("Query=%s\n" % aQry )
	return aQry

def Base64Encode(text):
	if sys.version_info >= (3,):
		return base64.urlsafe_b64encode(text.encode('utf-8')).decode('utf-8')
	else:
		return base64.urlsafe_b64encode(text)

def Base64Decode(text):
   try:
      if sys.version_info >= (3,):
         resu = base64.urlsafe_b64decode(text.encode('utf-8')).decode('utf-8')
      else:
         resu = base64.urlsafe_b64decode(str(text))
      return resu
   except Exception:
      exc = sys.exc_info()[1]
      sys.stderr.write("CANNOT DECODE: symbol=(%s):%s\n"%(text,str(exc)))
      return text + ":" + str(exc)

# Default destination for the RDF, HTML or SVG output.
def DfltOutDest(out_dest=None):
	if out_dest == None:
		if sys.version_info >= (3,):
			return sys.stdout.buffer
		else:
			return sys.stdout
	else:
		return out_dest

# So we try to load only once.
cacheEntityToModule = dict()

# Maybe we could return an array because of heritage ?
# Or:  GetEntityModuleFunction(entity_type,functionName):
# ... which would explore from bottom to top.
def GetEntityModule(entity_type):
	sys.stderr.write("GetEntityModule entity_type=%s\n"%entity_type)
	sys.stderr.write("PYTHONPATH="+os.environ['PYTHONPATH']+"\n")
	sys.stderr.write("sys.path="+str(sys.path)+"\n")

	try:
		# Might be None if the module does not exist.
		return cacheEntityToModule[ entity_type ]
	except KeyError:
		pass

	try:
		# Beware: No directories here, for the moment:
		# "revlib/lib_entities/lib_entity_dbus_connection.py"
		entity_lib = ".lib_entity_" + entity_type
		sys.stderr.write("Loading entity-specific library:"+entity_lib+"\n")
		entity_module = importlib.import_module( entity_lib, "lib_entities")
		sys.stderr.write("Loaded entity-specific library:"+entity_lib+"\n")
		return entity_module
	except ImportError:
		pass

	try:
		# Here, we want: "sources_types/Azure/location/__init__.py"
		# Example: entity_type = "Azure.location"
		# This works.
		# entity_module = importlib.import_module( ".subscription", "sources_types.Azure")

		# entity_type_split = ["Azure","subscription"]
		entity_type_split = entity_type.split("/")
		if len(entity_type_split) > 1:
			entity_package = "sources_types." + ".".join(entity_type_split[:-1])
			entity_name = "." + entity_type_split[-1]
		else:
			entity_package = "sources_types"
			entity_name = entity_type
		sys.stderr.write("Loading from new hierarchy entity_name=%s entity_package=%s\n:"%(entity_name,entity_package))
		entity_module = importlib.import_module( entity_name, entity_package)
		sys.stderr.write("Loaded OK from new hierarchy entity_name=%s entity_package=%s\n:"%(entity_name,entity_package))
		return entity_module

	except ImportError:
		pass

	sys.stderr.write("Info:Cannot find entity-specific library:"+entity_lib+"\n")
	entity_module = None

	return entity_module