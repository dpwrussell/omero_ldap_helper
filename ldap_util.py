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

        found = False
        for result in results:
            if result[0] is None:
                pass # Ignoring referral
            else:
                cn = result[1]['cn'][0]
                if cn.lower() == name.lower():
                    found = True
                else:
                    error_msg = '%s not found, but there were search results, should not happen' %name
                    raise Exception(error_msg)

        return found

    def userSearch(self, cn_user):
        filter = '(&(objectClass=user)(cn=%s))' %cn_user
        return self._search(filter, cn_user)

    def groupSearch(self, cn_group):
        filter = '(&(objectClass=group)(mail=omero.flag)(cn=%s))' %cn_group
        return self._search(filter, cn_group)

    def userEmailSearch(self, cn_email):
        filter = '(&(objectClass=user)(mail=%s))' %cn_email

        attrs = ['cn']

        results = self.l.search_s( self.basedn, ldap.SCOPE_SUBTREE, filter, attrs )

        found_cn = ""
        found_cn_n = 0
        for result in results:
            if result[0] is None:
                pass # Ignoring referral
            else:
                found_cn = result[1]['cn'][0]
                found_cn_n = found_cn_n + 1

        if found_cn_n > 0:
            return found_cn, found_cn_n
