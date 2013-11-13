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
ldapSearch = LDAPSearch(ldap_details)

# Check users
query = "from Experimenter"
experimenters = queryService.findAllByQuery(query, params)
print('Experimenters')

for experimenter in experimenters:

	output = '%s' %experimenter.omeName.getValue()
	if experimenter.email and experimenter.email.getValue().strip() != '':
		output = output + ', %s ' %experimenter.email.getValue()

	if len(ldapSearch.userSearch(experimenter.omeName.getValue())) == 1:
		output = output + ', OK'
	else:
		output = output + ', MISSING'
		if experimenter.email:
			
			cns = ldapSearch.userEmailSearch(experimenter.email.getValue())
			if len(cns) == 1:
				output = output + ' (Probably: %s)' %cns[0]
			elif len(cns) > 1:
				output = output + ' (Multiple users for this email address)'
	print output

# Check groups
query = "from ExperimenterGroup"
groups = queryService.findAllByQuery(query, params)
print('Groups')
for group in groups:

	output = '%s' %group.name.getValue()
	if group.description and group.description.getValue().strip() != '':
		output = output + ', (%s) ' %group.description.getValue()

	# Get other groups which might be appropriate
	cns = ldapSearch.groupSearch(group.name.getValue())
	found = False
	if len(cns) == 1:					# Just 1 group
		output = output + ', OK'
		found = True
	else:
		output = output + ', MISSING'

	# Check for similar group names
	cns = ldapSearch.groupSearch('*' + group.name.getValue() + '*')	
	if len(cns) > 1 or (found == False and len(cns) > 0):
		ouput = output + ' (Possible groups: ' + ','.join(cns)
		for cn in cns:
			output = output + ' %s '
		output = output + ')'

	print output