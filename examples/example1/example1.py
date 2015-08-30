import argparse
from datetime import datetime

from birdsql import *


class Group(DatabaseObject):
    _table_name = "group"

    def __init__(self, **kwargs):
        self.id = None
        self.name = ""
        self.admin_rights = False
        # Call this last to setup instance vars
        DatabaseObject.__init__(self, **kwargs)


class User(DatabaseObject):
    _table_name = "user"

    def __init__(self, **kwargs):
        self.id = None
        self.enabled = False
        self.group_id = 0
        self.username = ""
        self.password = ""
        self.email = ""
        self.allow_email = True
        self.last_access = None

        self._group = None
        # Call this last to setup instance vars
        DatabaseObject.__init__(self, **kwargs)

    def from_name(self, username):
        res = self.query_one(username=username)
        return res

    @property
    def group(self):
        # Lazy load group
        if self._group is None:
            self._group = Group().from_id(self.group_id)
        return self._group


def main(args):
    setup_sql(args.host, args.port, args.username, args.password, args.db_name)

    all_users = User().query_all()
    print "All Users:"
    for user in all_users:
        print "\t" + user.username

    bob = User().from_name("Bob")
    if bob.group.admin_rights:
        print "Bob is an admin!"
    else:
        print "Bob not NOT an admin!"
    bob.last_access = datetime.now()
    bob.update(["last_access"])

    # You can put whatever where arguments you want in the call to this function
    email_allowed = User().query_all(email_allowed=True)
    print "{0} users allow email".format(len(email_allowed))

    admins = User().raw_query_all("select * from user join group on group.id = user.group_id where group.admin_rights")
    print "Admins:"
    for admin in admins:
        print "\t" + admin.username


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--host", dest="host", default="localhost")
    parser.add_argument("-P", "--port", dest="port", default=3306, type=int)
    parser.add_argument("-u", "--username", dest="username", default="root")
    parser.add_argument("-p", "--password", dest="password", default="root")
    args = parser.parse_args()
    main(args)

