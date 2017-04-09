#!/usr/bin/python

"""
RabbitMQ queues on all virtual hosts
"""

import sys
import rdflib
import lib_common
import lib_credentials
from pyrabbit.api import Client
from sources_types import rabbitmq
from sources_types.rabbitmq import manager as survol_rabbitmq_manager
from sources_types.rabbitmq import queue as survol_rabbitmq_queue
from sources_types.rabbitmq import vhost as survol_rabbitmq_vhost

# It uses the port of the management interface:
# In rabbitmq.config:
# {rabbitmq_management,
#  [
#   {listener, [{port,     12345},
#               {ip,       "127.0.0.1"}]}

# rabbitmq-plugins enable rabbitmq_management

def Main():

	cgiEnv = lib_common.CgiEnv()

	configNam = cgiEnv.GetId()

	nodeManager = survol_rabbitmq_manager.MakeUri(configNam)

	creds = lib_credentials.GetCredentials( "RabbitMQ", configNam )

	# cl = Client('localhost:12345', 'guest', 'guest')
	cl = Client(configNam, creds[0], creds[1])

	grph = rdflib.Graph()

	# cl.is_alive()

	for quList in cl.get_queues():
		namQueue = quList["name"]
		sys.stderr.write("q=%s\n"%(namQueue))

		namVHost = quList["vhost"]
		nodVHost = survol_rabbitmq_vhost.MakeUri(configNam,namVHost)

		nodeQueue = survol_rabbitmq_queue.MakeUri(configNam,namVHost,namQueue)

		grph.add( ( nodeQueue, lib_common.MakeProp("vhost"), rdflib.Literal(namVHost) ) )
		grph.add( ( nodeQueue, lib_common.MakeProp("vhost node"), nodVHost ) )

		managementUrl = rabbitmq.ManagementUrlPrefix(configNam,"queues",namVHost,namQueue)

		grph.add( ( nodeQueue, lib_common.MakeProp("Management"), rdflib.URIRef(managementUrl) ) )


		grph.add( ( nodeManager, lib_common.MakeProp("Queue"), nodeQueue ) )


	cgiEnv.OutCgiRdf(grph)

if __name__ == '__main__':
	Main()