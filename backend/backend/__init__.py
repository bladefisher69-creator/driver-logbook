# Shim to allow Django's 'mysqlclient' expectation (MySQLdb) to work with PyMySQL on Windows.
# This file makes PyMySQL present itself as MySQLdb so Django's MySQL backend can import it.

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # If PyMySQL isn't installed, importing will raise; let Django raise a helpful error later.
    pass
