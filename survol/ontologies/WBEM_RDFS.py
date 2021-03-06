#!/usr/bin/env python

# This explores the classes of the WBEM server running on this machine
# and generates an RDFS ontology.

# It does not depend on a Survol installation.
# However, its classes and properties will overlap Survol's if it is installed.
# Also, because they use rdflib and wbem, it is simpler to share the same code.

import os

import lib_ontology_tools
import lib_export_ontology
import lib_kbase
import lib_wbem

def Main():
    # Il y a deux facons de le faire: Soit on se connecte sur la machine par notre agent
    # et on utilise WBEM en local,
    # ou bien on reste sur nre machine et on utilise le server WBEM.
    # map_classes, map_attributes = lib_wbem.ExtractWbemOntologyLocal()
    map_classes, map_attributes = lib_ontology_tools.ManageLocalOntologyCache( "wbem", lib_wbem.ExtractWbemOntology)
    graph = lib_kbase.CreateRdfsOntology(map_classes, map_attributes)

    onto_filnam = os.path.splitext(__file__)[0] + ".rdfs"
    lib_export_ontology.FlushOrSaveRdfGraph(graph,onto_filnam)

if __name__ == '__main__':
    Main()
