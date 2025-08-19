"""
AtlasLIBYA Django Project
"""

# PyMySQL compatibility shim - safely import only when needed
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    # PyMySQL is optional - only needed when using MySQL backend
    pass
