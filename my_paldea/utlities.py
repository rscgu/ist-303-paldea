from ldap3 import Server, Connection, ALL

LDAP_HOST = "localhost"
LDAP_PORT = 389
LDAP_USER = "cn=admin,dc=example,dc=com"
LDAP_PASSWORD = "secret"
LDAP_BASE_DN = "dc=example,dc=com"

def get_ldap_connection():
    server = Server(LDAP_HOST, port=LDAP_PORT, get_info=ALL)
    conn = Connection(server, user=LDAP_USER, password=LDAP_PASSWORD, auto_bind=True)
    return conn