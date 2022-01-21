import os
import sqlite3 as sl
from pprint import pprint


class ContactsDB(object):
    def __init__(self, db_path):
        if not os.path.isdir(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))

        self.db_path = db_path
        self.conn = sl.connect(db_path)
        self.conn.row_factory = sl.Row

    def create_table(self, table_name, columns):
        columns_str = """\nid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"""
        for key, val in columns.items():
            upper_val = val.upper()
            if upper_val not in ["TEXT", "INT", "INTEGER", "REAL", "NULL"]:
                raise Exception(
                    "Invalid Data type for Column:",
                )

            columns_str += ",\n" + key + " " + upper_val

        sql_command = """CREATE TABLE IF NOT EXISTS {0} ({1});""".format(
            table_name, columns_str
        )

        self.conn.execute(sql_command)
        self.conn.commit()

    def remove_table(self, table_name):
        sql_command = 'DROP TABLE ' + table_name
        self.conn.execute(sql_command)
        self.conn.commit()

    def does_table_exist(self, table_name):
        sql_command = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(
                table_name
            )
        )
        cursor = self.conn.execute(sql_command)
        result = len(cursor.fetchall())
        if result:
            return True

        return False

    def create(self, table_name, data):
        if not self.does_table_exist(table_name):
            raise Exception("Table " + table_name + " does not exist.")

        if not isinstance(data, dict):
            raise Exception("Invalid data type!")

        if "id" in data.keys():
            raise Exception("id field is immutable and cannot be set by user.")

        key_data = ", ".join(data.keys())
        val_data = ""
        for key in data.keys():
            if isinstance(data[key], str):
                val_data += "'" + data[key] + "', "
            elif isinstance(data[key], int):
                val_data += str(data[key]) + ", "
            else:
                val_data += "null, "

        val_data = val_data.rstrip(", ")
        sql_command = "INSERT INTO {0} ({1}) values({2})".format(
            table_name, key_data, val_data
        )
        self.conn.execute(sql_command)
        self.conn.commit()

    def find(self, table_name, filters, fields, operator="AND"):
        if not self.does_table_exist(table_name):
            raise Exception("Table " + table_name + " does not exist.")

        if not isinstance(filters, list):
            raise Exception("Invalid filter data type!")

        columns = self.get_table_columns(table_name)
        if not fields:
            fields = columns

        field_str = ", ".join(fields)
        fltr_list = []
        return_data = []

        for fltr in filters:
            if not isinstance(fltr, list):
                raise Exception("Invalid filter in filters!")

            if fltr[0] not in columns:
                raise Exception("Invalid filter field:" + fltr[0])

            if isinstance(fltr[2], str):
                if fltr[1] == "is":
                    fltr_string = fltr[0] + "='" + fltr[2] + "'"

                elif fltr[1] == "contains":
                    fltr_string = fltr[0] + " LIKE '%" + fltr[2] + "%'"

                else:
                    raise Exception("Invalid Condition for filter:" + str(fltr))

            if isinstance(fltr[2], int):
                if fltr[1] == "less_than":
                    fltr_string = fltr[0] + "<" + str(fltr[2])

                elif fltr[1] == "less_than_equal":
                    fltr_string = fltr[0] + "<=" + str(fltr[2])

                elif fltr[1] == "greater_than":
                    fltr_string = fltr[0] + ">" + str(fltr[2])

                elif fltr[1] == "greater_than_equal":
                    fltr_string = fltr[0] + "<" + str(fltr[2])

                elif fltr[1] == "equal":
                    fltr_string = fltr[0] + "=" + str(fltr[2])

                elif fltr[1] == "not_equal":
                    fltr_string = fltr[0] + "!=" + str(fltr[2])

                else:
                    raise Exception("Invalid Condition for filter:" + str(fltr))

            fltr_list.append(fltr_string)

        operator = " " + operator + " "
        fltr_string = operator.join(fltr_list)
        if fltr_string:
            sql_command = "SELECT {0} FROM {1} WHERE {2};".format(
                field_str, table_name, fltr_string
            )
        else:
            sql_command = "SELECT {0} FROM {1};".format(field_str, table_name)

        cursor = self.conn.cursor()
        rows = cursor.execute(sql_command)
        for row in rows:
            data_dict = {}
            for index in range(len(fields)):
                data_dict[fields[index]] = row[index]

            return_data.append(data_dict)

        return return_data

    def update(self, table_name, _id, data):
        update_data_str = ""
        columns = self.get_table_columns(table_name)

        for key, val in data.items():
            if key not in columns:
                raise Exception("Invalid Data Field")

            if key == "id":
                raise Exception("ID field is Immutable.")

            if isinstance(val, str):
                update_data_str += key + "='" + val + "', "

            elif isinstance(val, int):
                update_data_str += key + "=" + str(val) + ", "

        update_data_str = update_data_str.rstrip(", ")

        sql_command = "UPDATE {0} SET {1} WHERE id={2}".format(
            table_name, update_data_str, _id
        )
        self.conn.execute(sql_command)
        self.conn.commit()

    def delete(self, table_name, ids):
        sql_command = (
            "DELETE FROM " + table_name + " WHERE id IN " + str(tuple(ids)) + ";"
        )
        self.conn.execute(sql_command)
        self.conn.commit()

    def get_table_columns(self, table_name):
        sql_command = "SELECT * FROM " + table_name
        cursor = self.conn.execute(sql_command)
        row = cursor.fetchone()
        if row:
            names = row.keys()
            return names
        else:
            names = [description[0] for description in cursor.description]
            return names

    def close(self):
        self.conn.close()


# TESTS
test_contacts_db_conn = ContactsDB("C:/tmp/test.db")
# test_contacts_db_conn.create_table("BAD_CONTACTS", {
# 	"name": "TEXT",
# 	"address": "TEXT",
# 	"phone_number": "TEXT"
# 	})

# print(test_contacts_db_conn.does_table_exist('PERSONAL_CONTACTS'))
# test_contacts_db_conn.create('PERSONAL_CONTACTS',
# 	{
# 		"name": "Jasmine",
# 		"address": "11305, 240St",
# 		"phone_number": "236-688-4650"
# 	})

# test_contacts_db_conn.create('PERSONAL_CONTACTS',
# 	{
# 		"name": "Shobhit",
# 		"address": "11305, 240St",
# 		"phone_number": "236-688-6126"
# 	})

# test_contacts_db_conn.create('PERSONAL_CONTACTS',
# 	{
# 		"name": "Luna",
# 		"address": "11305, 240St",
# 	})

# test_contacts_db_conn.create('PERSONAL_CONTACTS',
# 	{
# 		"name": "Test",
# 		"address": "11305, 240St",
# })

# test_contacts_db_conn.delete('PERSONAL_CONTACTS', [31,32])

# test_contacts_db_conn.get_table_columns('PERSONAL_CONTACTS')

# pprint(test_contacts_db_conn.find('PERSONAL_CONTACTS',
# 	[
# 		['name', 'contains', 'S'],
# 		['phone_number', 'is', '236-688-6126']
# 	],
# 	['name', 'address', 'phone_number'],
# 	operator='OR'
# ))

# test_contacts_db_conn.update(
#     "PERSONAL_CONTACTS",
#     30,
#     {"name": "Shobhit Khinvasara", "address": "11305, 240St Maple Ridge"},
# )

# test_contacts_db_conn.remove_table("BAD_CONTACTS")
