"""
	Transforms an internal graph into a HTML page.
"""

import sys
import lib_util
import lib_common
import lib_exports
import lib_patterns
import lib_naming
import lib_kbase
import entity_dirmenu_only
import lib_properties
from lib_properties import pc


# Needed because of sockets.
def WrtAsUtf(str):
	out_dest = lib_util.DfltOutDest()

	# TODO: try to make this faster. Should be conditional just like HttpHeader.
	out_dest.write( str.encode('utf-8') )


def WriteScriptInformation(theCgi):
	"""
		This displays general information about this script and the object if there is one.
	"""
	sys.stderr.write("WriteScriptInformation entity_type=%s\n"%(theCgi.m_entity_type))

	# This is already called in lib_common, when creating CgiEnv.
	# It does not matter because this is very fast.
	callingUrl = lib_util.RequestUri()
	( entity_label, entity_graphic_class, entity_id ) = lib_naming.ParseEntityUri(callingUrl,longDisplay=True)
	sys.stderr.write("entity_label=%s entity_graphic_class=%s entity_id=%s\n"%( entity_label, entity_graphic_class, entity_id ))

	WrtAsUtf('<table class="list_of_merged_scripts">')
	if len(lib_common.globalCgiEnvList):
		sys.stderr.write("lib_common.globalCgiEnvList=%s\n"%str(lib_common.globalCgiEnvList))
		# This step is dedicated to the merging of several scripts.

		WrtAsUtf("<tr align=left><td colspan=2 align=left><b>Merge of %d scripts</b></td></tr>"%len(lib_common.globalCgiEnvList))
		for aCgiEnv in lib_common.globalCgiEnvList:
			sys.stderr.write("aCgiEnv=%s\n"%str(aCgiEnv))
			sys.stderr.write("aCgiEnv.m_page_title=%s\n"%str(aCgiEnv.m_page_title))
			sys.stderr.write("aCgiEnv.m_calling_url=%s\n"%str(aCgiEnv.m_calling_url))
			(page_title_first,page_title_rest) = lib_util.SplitTextTitleRest(aCgiEnv.m_page_title)
			WrtAsUtf("<tr><td><a href='%s'>%s</td><td><i>%s</i></td></tr>"%(aCgiEnv.m_calling_url,page_title_first,page_title_rest))


		# Voir theCgiEnv.m_page_title dans MergeOutCgiRdf()
		# On pourrait lister les scripts mais ce serait aussi interessant de le faire en mode SVG,
		# dans la legende.
	else:
		(page_title_first,page_title_rest) = lib_util.SplitTextTitleRest(theCgi.m_page_title)
		WrtAsUtf("<tr><td colspan=2>%s</td></tr>"%(page_title_first))
		if page_title_rest:
			WrtAsUtf("<tr><td colspan=2>%s</td></tr>"%(page_title_rest))
		#WrtAsUtf("<tr align=left><td colspan=2 align=left><b>%s</b></td></tr>"%theCgi.m_page_title.strip())

	WrtAsUtf('</table>')

	# This is the entire content, not only the first line.
	#theDoc = lib_common.GetCallingModuleDoc()
	#theDoc = theDoc.replace("\n","<br>")
	#WrtAsUtf('<i><h2>NON  C ESR PAS LE BON %s</h2></i>'%(theDoc))
	#WrtAsUtf('<i><h2>NON  C ESR PAS LE BON %s</h2></i>'%(theCgi.m_page_title))

	if theCgi.m_entity_type:
		# WrtAsUtf('m_entity_id: %s<br>'%(theCgi.m_entity_id))

		WrtAsUtf('<table class="table_script_information">')

		entity_module = lib_util.GetEntityModule(theCgi.m_entity_type)
		entDoc = entity_module.__doc__
		if not entDoc:
			entDoc = ""
		# WrtAsUtf('Module class: %s: %s<br>'%(theCgi.m_entity_type,entDoc))

		urlClass = lib_util.EntityClassUrl(theCgi.m_entity_type)

		WrtAsUtf(
		"""
		<tr>
			<td><a href='%s'>%s</a></td>
			<td>%s</td>
		</tr>
		"""
		% ( urlClass, theCgi.m_entity_type, entDoc ))

		for keyProp in theCgi.m_entity_id_dict:
			keyVal = theCgi.m_entity_id_dict[keyProp]

			WrtAsUtf(
			"""
			<tr>
				<td>%s</td>
				<td>%s</td>
			</tr>
			"""
			% ( keyProp, keyVal ))

		WrtAsUtf('</table>')



# TODO: Fix this.
def WriteParameters(parameters):
	"""
		This displays the parameters of the script and provide an URL to edit them.
	"""
	WrtAsUtf('<table class="table_script_parameters">')

	WrtAsUtf('<tr><td colspan="2"><a href="' + lib_exports.ModedUrl("edit") + '">CGI parameters edition</a></td></tr>')

	for keyParam,valParam in parameters.items():
		WrtAsUtf(
		"""
		<tr>
			<td><b>%s</b></td>
			<td>%s</td>
		</tr>
		"""
		% ( keyParam, str(valParam) ))


	WrtAsUtf('</table>')

def WriteOtherUrls(topUrl):
	"""
		This displays the URL to view the same document, in other ouput formats.
	"""

	WrtAsUtf('<table class="other_urls">')

	if topUrl:
		WrtAsUtf("""
		<tr><td align="left" colspan="2"><a href="%s"><b>Home</b></a></td></tr>
		""" % topUrl )

	WrtAsUtf("""
	<tr>
		<td class="other_urls"><a href="%s">Content as SVG</a></td>
		<td>This displays the same content, in SVG format, generated by Graphviz</td>
	</tr>
	""" % lib_exports.ModedUrl("svg") )

	WrtAsUtf("""
	<tr>
		<td class="other_urls"><a href="%s">Content as RDF</a></td>
		<td>Same content, in RDF format, compatible with Semantic Web OWL standards, to be loaded by software such as Protege, etc...</td>
	</tr>
	""" % lib_exports.ModedUrl("rdf") )

	urlD3 = lib_exports.UrlToMergeD3()

	WrtAsUtf("""
	<tr>
		<td class="other_urls"><a href="%s">Content as D3</a></td>
		<td>Same content, displayed in Javascript D3 library</td>
	</tr>
	""" % urlD3 )

	WrtAsUtf('</table>')



def WriteScriptsTree(theCgi):
	"""
		This displays the tree of accessible Python scripts for the current object.
		It is dsiplayed as a recusive tab. A similar logic is used in entity.y
		(Where the tree is displayed as a tree of SVG nodes) and in index.htm
		(With a contextual menu).
	"""
	flagShowAll = False
	rootNode = None

	dictScripts = {}

	def CallbackGrphAdd( trpl, depthCall ):
		subj,prop,obj = trpl

		# sys.stderr.write("CallbackGrphAdd subj=%s\n"%str(subj))
		try:
			mapProps = dictScripts[subj]
			try:
				lstObjs = mapProps[prop].append(obj)
			except KeyError:
				mapProps[prop] = [obj]
		except KeyError:
			dictScripts[subj] = { prop : [obj ] }

	sys.stderr.write("WriteScriptsTree entity_type=%s\n"%(theCgi.m_entity_type))
	entity_dirmenu_only.DirToMenu(CallbackGrphAdd,rootNode,theCgi.m_entity_type,theCgi.m_entity_id,theCgi.m_entity_host,flagShowAll)

	sys.stderr.write("dictScripts %d\n"%len(dictScripts))


	def DisplayLevelTable(subj,depthMenu=1):
		"""
			Top-level should always be none.
			TODO: Have another version which formats all cells the same way.
			For this, have a first pass which counts, at each node, the number of sub-nodes.
			Then a second pass which uses thiese counts and the current depth,
			to calculate the rowspan and colspan of each cell.
			Although elegant, it is not garanteed to work.
		"""
		WrtAsUtf('<table class="table_scripts_titles">')
		try:
			mapProps = dictScripts[subj]
		except KeyError:
			return

		def ExtractTitleFromMapProps(mapProps):
			if len(mapProps) != 1:
				return None
			for oneProp in mapProps:
				if oneProp != pc.property_information:
					return None

				lstStr = mapProps[oneProp]
				if len(lstStr) != 1:
					return None
				retStr = lstStr[0]
				if lib_kbase.IsLink( retStr ):
					return None

				return str(retStr)

		WrtAsUtf('<tr>')
		depthMenu += 1

		subj_uniq_title = ExtractTitleFromMapProps(mapProps)

		if subj:
			subj_str = str(subj)
			WrtAsUtf("<td rowspan='%d'>"%len(mapProps))
			if lib_kbase.IsLink( subj ):
				url_with_mode = lib_util.ConcatenateCgi( subj_str, "mode=html" )
				WrtAsUtf( '<a href="' + url_with_mode + '">' + subj_uniq_title + "</a>")
			else:
				WrtAsUtf( subj_str )
			WrtAsUtf("</td>")

		if not subj_uniq_title:
			for oneProp in mapProps:
				lstObjs = mapProps[oneProp]

				WrtAsUtf('<td>')
				WrtAsUtf('<table class="table_scripts_links">')
				for oneObj in lstObjs:
					if oneObj is None:
						continue
					WrtAsUtf('<tr>')
					WrtAsUtf('<td>')
					try:
						mapPropsSub = dictScripts[oneObj]
						DisplayLevelTable(oneObj,depthMenu)
					except KeyError:
						WrtAsUtf("Script error: "+str(oneObj))
					WrtAsUtf('</td>')
					WrtAsUtf('</tr>')
				WrtAsUtf('</table>')
				WrtAsUtf('</td>')

		WrtAsUtf('</tr>')
		WrtAsUtf( "</table>")

	DisplayLevelTable(None)

	# TODO: Add this.
	#if entity_type != "":
	#	sys.stderr.write("Entering AddWbemWmiServers\n")
	#	CIM_ComputerSystem.AddWbemWmiServers(grph,rootNode, entity_host, nameSpace, entity_type, entity_id)

	#AddDefaultScripts(grph,rootNode,entity_host)

	# Special case if we are displaying a machine, we might as well try to connect to it.
	#if entity_type == "CIM_ComputerSystem":
	#	AddDefaultScripts(grph,rootNode,entity_id)


def WriteErrors(error_msg,isSubServer):
	if error_msg or isSubServer:
		# TODO: Use style-sheets.
		WrtAsUtf('<table border="0">')

		if error_msg:
			WrtAsUtf('<tr><td bgcolor="#DDDDDD" align="center" color="#FF0000"><b></b></td></tr>')
			WrtAsUtf('<tr><td bgcolor="#DDDDDD"><b>ERROR MESSAGE:%s</b></td></tr>' % error_msg)

		if isSubServer:
			WrtAsUtf('<tr><td><a href="' + lib_exports.ModedUrl("stop") + '">Stop subserver</a></td></tr>')
		WrtAsUtf( " </table><br>")


def WriteAllObjects(grph):
	"""
		This displays all the objects returend by this scripts.
		Other scripts are not here, so we do not have to eliminate them.
		This is therefore simpler than in the SVG (Graphviz) output,
		where all objects are mixed together.
	"""


	# This groups data by subject, then predicate, then object.
	dictClassSubjPropObj = dict()

	# TODO: Group objects by type, then display the count, some info about each type etc...
	for aSubj, aPred, anObj in grph:
		# No point displaying some keys if there is no value.
		if aPred == pc.property_information :
			try:
				if str(anObj) == "":
					continue
			# 'ascii' codec can't encode character u'\xf3' in position 17: ordinal not in range(128)
			# u'SDK de comprobaci\xf3n de Visual Studio 2012 - esn'
			except UnicodeEncodeError:
				exc = sys.exc_info()[1]
				sys.stderr.write("Exception %s\n"%str(exc))
				continue

		subj_str = str(aSubj)
		( subj_title, entity_graphic_class, entity_id ) = lib_naming.ParseEntityUri(subj_str)

		try:
			dictSubjPropObj = dictClassSubjPropObj[entity_graphic_class]
			try:
				dictPred = dictSubjPropObj[aSubj]
				try:
					dictPred[aPred].append(anObj)
				except KeyError:
					# First time this object has this predicate.
					dictPred[aPred] = [ anObj ]
			except KeyError:
				# First time we see this object.
				dictSubjPropObj[aSubj] = { aPred : [ anObj ] }
		except KeyError:
			# First object of this class.
			dictClassSubjPropObj[entity_graphic_class] = { aSubj: { aPred : [ anObj ] } }

	# Group objects by class.
	# Display list of classes with an indexs and a link to the class.
	# "NO TITLE" is wrong
	# Trier par le nom.

	# Ajouter mode "difference": On recalcule periodiquement et on affiche la difference.


	for entity_graphic_class in dictClassSubjPropObj:

		# EntityClassUrl(entity_graphic_class, entity_namespace = "", entity_host = "", category = ""):
		urlClass = lib_util.EntityClassUrl(entity_graphic_class)

		WrtAsUtf("<h3/>Class <a href='%s'>%s</a><h2/>"%(urlClass,entity_graphic_class))
		dictSubjPropObj = dictClassSubjPropObj[entity_graphic_class]

		DispClassObjects(dictSubjPropObj)

def DispClassObjects(dictSubjPropObj):
	listPropsTdDoubleColSpan = [pc.property_information,pc.property_rdf_data_nolist2,pc.property_rdf_data_nolist1]

	WrtAsUtf('<table class="class_objects">')
	for aSubj in dictSubjPropObj:
		dictPred = dictSubjPropObj[aSubj]

		subj_str = str(aSubj)
		( subj_title, entity_graphic_class, entity_id ) = lib_naming.ParseEntityUri(subj_str)

		arrayGraphParams = lib_patterns.TypeToGraphParams(entity_graphic_class)
		# "Graphic_shape","Graphic_colorfill","Graphic_colorbg","Graphic_border","Graphic_is_rounded"
		colorClass = arrayGraphParams[1]


		# Total number of lines.
		cntPreds = 0
		for aPred in dictPred:
			lstObjs = dictPred[aPred]
			cntPreds += len(lstObjs)

		mustWriteColOneSubj = True

		# TODO: The second sort key should be the value.
		for aPred in sorted(dictPred):
			lstObjs = dictPred[aPred]

			predStr = lib_exports.AntiPredicateUri(str(aPred))
			cntObjs = len(lstObjs)
			mustWriteColOnePred = True

			for anObj in lstObjs:

				WrtAsUtf( '<tr bgcolor="' + colorClass + '">' )

				if mustWriteColOneSubj:
					WrtAsUtf(
						'<td rowspan="' + str(cntPreds) + '">'
						+'<a href="' + subj_str + '">'+ subj_title + "</a>"
						# + " (" + entity_graphic_class + ")"
						+ "</td>")
					mustWriteColOneSubj = False

				if mustWriteColOnePred:
					# if aPred != pc.property_information :
					if aPred not in listPropsTdDoubleColSpan :
						WrtAsUtf( '<td rowspan="' + str(cntObjs) + '">'+ predStr + "</td>")
					mustWriteColOnePred = False

				obj_str = str(anObj)

				if aPred in listPropsTdDoubleColSpan:
					colSpan = 2
				else:
					colSpan = 1

				if lib_kbase.IsLink( anObj ):
					obj_title = lib_naming.ParseEntityUri(obj_str)[0]
					url_with_mode = lib_util.ConcatenateCgi( obj_str, "mode=html" )
					WrtAsUtf( '<td colSpan="%d"><a href="%s">%s</a></td>' % (colSpan,url_with_mode,obj_title))
				else:
					WrtAsUtf( '<td colspan="%d">%s</td>' %(colSpan,obj_str))

				WrtAsUtf( "</tr>")

	WrtAsUtf( " </table>")

def Grph2Html( theCgi, topUrl, error_msg, isSubServer):
	"""
		This transforms an internal data graph into a HTML document.
	"""
	page_title = theCgi.m_page_title
	grph = theCgi.m_graph
	parameters = theCgi.m_parameters

	lib_util.WrtHeader('text/html')
	WrtAsUtf( "<head>" )

	# TODO: Encode HTML special characters.
	WrtAsUtf( "<title>" + page_title + "</title>")

	# The href must be absolute so it will work with any script.
	# We must calculate its prefix.
	# In the mean time, this solution adapts to our three kind of different hosting types:
	# - OVH mutialised hosting, with a specific CGI script survol.cgi
	# - With the Python class HttpServer as Web server.
	# - Hosted with Apache.
	WrtAsUtf(
		"""
		<link rel='stylesheet' type='text/css' href=/ui/css/html_exports.css>
		<link rel='stylesheet' type='text/css' href='/survol/www/css/html_exports.css'>
		<link rel='stylesheet' type='text/css' href='../survol/www/css/html_exports.css'>
		""")

	WrtAsUtf('</head>')

	WrtAsUtf('<body>')

	WriteScriptInformation(theCgi)

	WriteErrors(error_msg,isSubServer)

	WrtAsUtf("<h2/>Objects<h2/>")
	WriteAllObjects(grph)

	if len(parameters) > 0:
		WrtAsUtf("<h2/>Script parameters<h2/>")
		WriteParameters(parameters)

	WrtAsUtf("<h2/>Other related urls<h2/>")
	WriteOtherUrls(topUrl)

	# Scripts do not apply when displaying a class.
	# TODO: When in a enumerate script such as enumerate_CIM_LogicalDisk.py,
	# it should assume the same: No id but a class.
	if(theCgi.m_entity_type == "") or (theCgi.m_entity_id!=""):
		WrtAsUtf("<h2/>Related data scripts<h2/>")
		WriteScriptsTree(theCgi)

	WrtAsUtf("</body>")

	WrtAsUtf("</html> ")

################################################################################
