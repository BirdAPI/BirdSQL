from pprint import pprint, pformat
from collections import defaultdict

import birdsql


class ConnectionInfo(object):
    def __init__(self, host="", port=3306, user="", password="", db_name=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name


class DatabaseObject(object):
    _table_name = None
    _id_column = "id"
    _ignore_list = [ _id_column ]

    def __init__(self, _strict_mode=False, **kwargs):
        """
        Pass in whatever instance variables you want set as kwargs.
        This can be called from any subclass in order to easily
        create instance objects. This should be called last
        as to prevent values being overridden with None.
        @strict_mode makes it so that only values that are
        already defined (usually set to None) can be set.
        --- this:
        obj = DatabaseObject()
        obj.id = 5
        obj.name = 'string'
        --- becomes:
        obj = DatabaseObject(id=5, name='string')
        """
        for key, val in kwargs.items():
            if not _strict_mode or key in self.__dict__:
                self.__dict__[key] = val

    def get_id(self):
        return self.__dict__[self._id_column]

    def set_id(self, val):
        self.__dict__[self._id_column] = val

    def dump(self):
        pprint(self.__dict__)

    def dump_str(self):
        return pformat(self.__dict__)

    def insert(self, replace_into=False):
        """
        Insert this item into the database, optionally "REPLACE INTO"
        """
        return birdsql._get_db().insert_generic(self, replace_into=replace_into)

    def insert_or_update(self):
        return birdsql._get_db().insert_or_update_generic(self)

    def update_full(self):
        return birdsql._get_db().update_generic_full(self)

    def update(self, what_list=None):
        return birdsql._get_db().update_generic(self, what_list)

    def delete(self):
        return birdsql._get_db().delete_generic(self)

    def from_id(self, id, include_extras=False):
        kwargs = { self._id_column : id }
        return self.query_one(include_extras=include_extras, **kwargs)

    def query_all(self, limit=None, order_by=None, include_extras=False, _log=False, **kwargs):
        #TODO: Does kwargs.keys() and kwargs.values() return items in the same order?
        where_clause = limit_clause = order_clause = ''
        values = []
        if kwargs is not None and len(kwargs.keys()) > 0:
            where_parts = []
            for key, value in kwargs.items():
                where_part, use_value = self.get_where_part(key, value)
                where_parts.append(where_part)
                if use_value:
                    values.append(value)
            where_clause = ' where ' + ' and '.join(where_parts)
        if limit is not None:
            limit_clause = ' limit {0} '.format(limit)
        if order_by is not None:
            order_clause = ' order by {0} '.format(order_by) if not order_by.strip().startswith('order') else order_by
        query = 'select * from `{0}` {1} {2} {3} '.format(self._table_name, where_clause, order_clause, limit_clause)
        if _log:
            print query
            pprint(kwargs)
        rows = birdsql._get_db().fetch_all(query, tuple(values))
        if _log:
            print 'Total rows returned:', len(rows)
        return self._create_objects(rows, include_extras)

    """
    Returns (where_part, use_value)
    """
    def get_where_part(self, key, value):
        if value is None:
            return '`{0}` is NULL'.format(key), False
        elif key.endswith("_like_"):
            return '`{0}` like %s'.format(key.replace("_like_", "")), True
        elif key.endswith("_null_"):
            return '`{0}` is {1}NULL'.format(key.replace("_null_", ""), "" if value else "not "), False
        else:
            return '`{0}`=%s'.format(key), True

    def query_one(self, order_by=None, include_extras=False, _log=False, **kwargs):
        all = self.query_all(limit=1, order_by=order_by, include_extras=include_extras, _log=_log, **kwargs)
        res = all[0] if all is not None else None
        if _log:
            res.dump()
        return res

    def raw_query_one(self, query, values, include_extras=False):
        row = birdsql._get_db().fetch_one(query, values)
        return self._create_object(row, include_extras)

    def raw_query_all(self, query, values, include_extras=False):
        rows = birdsql._get_db().fetch_all(query, values)
        return self._create_objects(rows, include_extras)

    def _create_objects(self, rows, include_extras=False):
        if rows is None or len(rows) == 0:
            return None
        else:
            return [ birdsql._get_db().get_generic(self.__class__(), row, include_extras) for row in rows ]

    def _create_object(self, row, include_extras=False):
        return birdsql._get_db().get_generic(self, row, include_extras)

    def query_all_grouped(self, group_col, limit=None, order_by=None, include_extras=False, _log=False, **kwargs):
        all = self.query_all(limit=limit, order_by=order_by, include_extras=include_extras, _log=_log, **kwargs)
        res = defaultdict(list)
        for item in all:
            key = item.__dict__[group_col]
            res[key].append(item)
        return res

