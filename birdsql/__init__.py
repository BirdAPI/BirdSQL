from datatypes import *
from db_mysql import *

_db = None


def setup_sql(host="", port=3306, user="", password="", db_name=""):
    global _db
    _db = MySqlHelper(ConnectionInfo(host, port, user, password, db_name))


def _get_db():
    return _db
