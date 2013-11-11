import ConfigParser

from omero.gateway import BlitzGateway
from omero.sys import Parameters

from ldap_util import LDAPSearch

# OMERO and LDAP Detail Configs
omero_details = 'omero_details.cfg'
ldap_details = 'ldap_details.cfg'

config = ConfigParser.RawConfigParser()
config.read(omero_details)

HOST = config.get('OMERODetails', 'host')
PORT = config.getint('OMERODetails', 'port')
USERNAME = config.get('OMERODetails', 'username')
PASSWORD = config.get('OMERODetails', 'password')

conn = BlitzGateway(USERNAME, PASSWORD, host=HOST, port=PORT)
connected = conn.connect()

if not connected:
    import sys
    sys.stderr.write("Error: Connection not available, please check your user name and password.\n")
    sys.exit(1)

session = conn.getSession()


queryService = conn.getQueryService()

params = Parameters()
query = "from Experimenter"


experimenters = queryService.findAllByQuery(query, params)

ldapSearch = LDAPSearch(ldap_details)

for experimenter in experimenters:

	output = '%s' %experimenter.omeName.getValue()
	if experimenter.email:
		output = output + ', %s ' %experimenter.email.getValue()

	if ldapSearch.userSearch(experimenter.omeName.getValue()):
		output = output + ', OK'
	else:
		output = output + ', MISSING'
		if experimenter.email:
			
			cn = ldapSearch.userEmailSearch(experimenter.email.getValue())
			if cn is not None:

				if cn[1] == 1:
					output = output + ' (Probably: %s)' %cn[0]
				elif cn[1] > 1:
					output = output + ' (Multiple users for this email address)'
	print output
