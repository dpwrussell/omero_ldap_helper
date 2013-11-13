import ConfigParser

import ldap

class LDAPSearch(object):

    def __init__(self, ldap_details):
        config = ConfigParser.RawConfigParser()
        config.read(ldap_details)

        self.username = config.get('LDAPDetails', 'username')
        self.password = config.get('LDAPDetails', 'password')
        self.server = config.get('LDAPDetails', 'server')
        self.basedn = config.get('LDAPDetails', 'basedn')

        self.l = ldap.initialize('ldaps://bioch-ad3.bioch.ox.ac.uk')

        self.l.protocol_version = ldap.VERSION3
        self.l.simple_bind_s(self.username, self.password)

    def _search(self, filter, name):

        attrs = ['cn']

        results = self.l.search_s( self.basedn, ldap.SCOPE_SUBTREE, filter, attrs )

        found = []
        for result in results:
            if result[0] is None:
                pass # Ignoring referral
            else:
                cn = result[1]['cn'][0]
                found.append(cn)

        return found

    def userSearch(self, cn_user):
        filter = '(&(objectClass=user)(cn=%s))' %cn_user
        return self._search(filter, cn_user)

    def groupSearch(self, cn_group):
        filter = '(&(objectClass=group)(mail=omero.flag)(cn=%s))' %cn_group
        return self._search(filter, cn_group)

    def userEmailSearch(self, cn_email):
        filter = '(&(objectClass=user)(mail=%s))' %cn_email
        return self._search(filter, cn_email)
