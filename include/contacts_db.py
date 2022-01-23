import os
import sqlite3 as sl
from pprint import pprint

class ContactsDB(object):
    def __init__(self, db_path):
        if db_path != ':memory:':
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
                self.conn.close()
                raise Exception(
                    "Invalid Data type for Column:",
                )

            columns_str += ",\n" + key + " " + upper_val

        sql_command = """CREATE TABLE IF NOT EXISTS {0} ({1});""".format(
            table_name, columns_str
        )
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            print('Database Operation Failed:', sql_command)
            self.close()
            return False

    def delete_table(self, table_name):
        sql_command = 'DROP TABLE ' + table_name
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close()
            return False

    def does_table_exist(self, table_name):
        sql_command = (
            "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(
                table_name
            )
        )
        try:
            cursor = self.conn.execute(sql_command)
            result = len(cursor.fetchall())
            if result:
                return True

            return False

        except:
            print('Database Operation Failed:', sql_command)
            return None

    def list_tables(self):
        sql_command = (
            "SELECT name FROM sqlite_master WHERE type='table';")
        try:
            cursor = self.conn.execute(sql_command)
            result = [res[0] for res in cursor.fetchall()]
            return result

        except:
            print('Database Operation Failed:', sql_command)
            return None

    def add(self, table_name, data):
        if not self.does_table_exist(table_name):
            self.conn.close()
            raise Exception("Table " + table_name + " does not exist.")

        if not isinstance(data, dict):
            self.conn.close()
            raise Exception("Invalid data type!")

        if "id" in data.keys():
            self.conn.close()
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
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            print('Database Operation Failed:', sql_command)
            return False

    def find(self, table_name, filters, fields, operator="AND"):
        if not self.does_table_exist(table_name):
            self.conn.close()
            raise Exception("Table " + table_name + " does not exist.")

        if not isinstance(filters, list):
            self.conn.close()
            raise Exception("Invalid filter data type!")

        columns = self.get_table_columns(table_name)
        if not fields:
            fields = columns

        field_str = ", ".join(fields)
        fltr_list = []
        return_data = []

        for fltr in filters:
            if not isinstance(fltr, list):
                self.conn.close()
                raise Exception("Invalid filter in filters!")

            if fltr[0] not in columns:
                self.conn.close()
                raise Exception("Invalid filter field:" + fltr[0])

            if isinstance(fltr[2], str):
                if fltr[1] == "is":
                    fltr_string = fltr[0] + "='" + fltr[2] + "'"

                elif fltr[1] == "contains":
                    fltr_string = fltr[0] + " LIKE '%" + fltr[2] + "%'"

                elif fltr[1] == "does_not_contain":
                    fltr_string = "NOT (" + fltr[0] + " LIKE '%" + fltr[2] + "%')"

                else:
                    self.conn.close()
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

                elif fltr[1] == "equals":
                    fltr_string = fltr[0] + "=" + str(fltr[2])

                elif fltr[1] == "not_equal":
                    fltr_string = fltr[0] + "!=" + str(fltr[2])

                else:
                    self.conn.close()
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

        try:
            cursor = self.conn.cursor()
            rows = cursor.execute(sql_command)
        except:
            print('Database Operation Failed:', sql_command)
            return False

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
                self.conn.close()
                raise Exception("Invalid Data Field")

            if key == "id":
                self.conn.close()
                raise Exception("ID field is Immutable.")

            if isinstance(val, str):
                update_data_str += key + "='" + val + "', "

            elif isinstance(val, int):
                update_data_str += key + "=" + str(val) + ", "

        update_data_str = update_data_str.rstrip(", ")

        sql_command = "UPDATE {0} SET {1} WHERE id={2}".format(
            table_name, update_data_str, _id
        )
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close()
            return False

    def delete(self, table_name, ids):
        if not ids:
            raise Exception("No ID specified.")
        if len(ids) == 1:
            sql_command = (
                "DELETE FROM " + table_name + " WHERE id=" + str(ids[0]) + ";"
            )
        else:
            sql_command = (
                "DELETE FROM " + table_name + " WHERE id IN " + str(tuple(ids)) + ";"
            )
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close()
            return False

    def get_table_columns(self, table_name):
        sql_command = "SELECT * FROM " + table_name
        try:
            cursor = self.conn.execute(sql_command)
        except:
            print('Database Operation Failed:', sql_command)
            return False

        row = cursor.fetchone()
        if row:
            names = row.keys()
            return names
        else:
            names = [description[0] for description in cursor.description]
            return names

    def clear_all_data(self, table_name):
        sql_command = (
            "DELETE FROM " + table_name + ";"
        )
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close()
            return False

    def close(self):
        self.conn.close()


