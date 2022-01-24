"""Constact Application Database API Using SQLite3 Module

Author: Shobhit Khinvasara
"""
import os
import sqlite3 as sl
from pprint import pprint
import traceback


class TypeMismatchError(Exception):
    """Error Class for Type Mismatch for filters or data."""

    pass


class TableError(Exception):
    """Error Class for Table creation and deletion."""

    pass


class IDError(Exception):
    """Error Class for ID Change."""

    pass


class InvalidFilterError(Exception):
    """Error Class for Invalid Filters."""

    pass


class DatabaseError(Exception):
    """Error Class for Generic Database Failures."""

    pass


class ContactsDB(object):
    """Contact Application Database API.

    Attributes:
        conn (SQLite Connection Object): Database Connection Object
        db_path (string): Path to the Database file.
    """

    def __init__(self, db_path):
        """Initializes Database.

        This is either by creating a new SQLite Database file or using an existing one.

        Args:
            db_path (string): Path to Local SQLite Database.
        """
        if db_path != ":memory:":
            if not os.path.isdir(os.path.dirname(db_path)):
                os.makedirs(os.path.dirname(db_path))

        self.db_path = db_path
        try:
            self.conn = sl.connect(db_path)
            self.conn.row_factory = sl.Row
        except:
            traceback.print_exc()
            raise DatabaseError("Database couldn't be initialized.")

    def create_table(self, table_name, fields):
        """This will create table <table_name> of specified fields.

        An Int type ID field will always be created by default.

        Args:
            table_name (string): Table Name.
            fields (dict): Dictionary where key is the field name and value is field type.
                            Supported field-type values are (Text, Integer).

        Returns:
            bool: True if Successful. False if not.

        """
        fields_str = """\nid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"""
        for key, val in fields.items():
            upper_val = val.upper()
            if upper_val not in ["TEXT", "INTEGER"]:
                self.close_conn()
                raise TypeMismatchError(
                    "Invalid Data type for Field: " + key + ":" + upper_val
                )

            fields_str += ",\n" + key + " " + upper_val

        tables = self.list_tables()
        if table_name in tables:
            self.close_conn()
            raise TableError("Table:", table_name, "already exists.")

        sql_command = """CREATE TABLE {0} ({1});""".format(table_name, fields_str)
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            print("Database Operation Failed:", sql_command)
            self.close_conn()
            return False

    def delete_table(self, table_name):
        """This will remove table <table_name> if exists.

        Args:
            table_name (string): Table Name.

        Returns:
            bool: True if Successful. False if not.

        """
        tables = self.list_tables()
        if table_name not in tables:
            self.close_conn()
            raise TableError("Table:" + table_name + " not found.")

        sql_command = "DROP TABLE " + table_name
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close_conn()
            return False

    def does_table_exist(self, table_name):
        """Check if table exists.

        Args:
            table_name (string): Table Name.

        Returns:
            TYPE: True if it does. False if it doesn't. NoneType if operation fails.
        """
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
            print("Database Operation Failed:", sql_command)
            return None

    def list_tables(self):
        """Display all tables in the Database.

        Returns:
            list: list of table names. NoneType if operation failed.
        """
        sql_command = "SELECT name FROM sqlite_master WHERE type='table';"
        try:
            cursor = self.conn.execute(sql_command)
            result = [res[0] for res in cursor.fetchall()]
            return result

        except:
            print("Database Operation Failed:", sql_command)
            return None

    def add(self, table_name, data):
        """Add Data to Database.

        Args:
            table_name (string): Table Name.
            data (dict): Dictionary containing {field:value}

        Returns:
            bool: True if Successful. False if not.

        """
        if not self.does_table_exist(table_name):
            self.conn.close()
            raise TableError("Table " + table_name + " does not exist.")

        if not isinstance(data, dict):
            self.conn.close()
            raise TypeMismatchError(
                "Invalid type of data arg. data arg needs to be a dict type."
            )

        if "id" in data.keys():
            self.conn.close()
            raise IDError("ID field is immutable and cannot be set by user.")

        key_str = ", ".join(data.keys())
        val_str = ""

        all_fields = self.get_table_fields(table_name)

        for key in data.keys():
            if key not in all_fields.keys():
                continue

            val = data[key]

            if isinstance(val, str):
                # check if type is string but acceptable type is integer.
                if all_fields[key] == "INTEGER":
                    self.close_conn()
                    raise TypeMismatchError(
                        "Invalid data type for:" + data[key] + ":" + val
                    )

                val_str += "'" + val + "', "

            elif isinstance(val, int):
                # check if type is integer but acceptable type is string.
                if all_fields[key] == "TEXT":
                    self.close_conn()
                    raise TypeMismatchError(
                        "Invalid data type for:" + data[key] + ":" + val
                    )

                val_str += str(val) + ", "

        val_str = val_str.rstrip(", ")
        sql_command = "INSERT INTO {0} ({1}) values({2})".format(
            table_name, key_str, val_str
        )
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            print("Database Operation Failed:", sql_command)
            return False

    def find(self, table_name, filters=[], fields=[], operator="AND"):
        """Summary

        Args:
            table_name (string): Table Name.
            filters (list, optional): List of filters. Example: [["name", "is", "ABC"]..]
                Valid Operators for Strings: is, is_not, contains, does_not_contain.
                Valid Operators for Integers: less_than, less_than_equal, greater_than, greater_than_equal, equals, not_equal.
            fields (list, optional): List of fields. Example: ["name", "address", "phone_number"]
            operator (str, optional): Operator for filters. Supported Operators: AND and OR

        Returns:
            TYPE: Description
        """
        if not self.does_table_exist(table_name):
            self.conn.close()
            raise TableError("Table " + table_name + " does not exist.")

        if not isinstance(filters, list):
            self.conn.close()
            raise TypeMismatchError("Invalid filter data type.")

        all_fields = self.get_table_fields(table_name)
        if not fields:
            fields = list(all_fields.keys())

        field_str = ", ".join(fields)
        fltr_list = []
        return_data = []

        for fltr in filters:
            if not isinstance(fltr, list):
                self.conn.close()
                raise TypeMismatchError("Invalid filter data type in filters.")

            if fltr[0] not in all_fields.keys():
                continue

            if isinstance(fltr[2], str):
                # check if type is string but acceptable type is integer.
                if all_fields[fltr[0]] == "INTEGER":
                    self.close_conn()
                    raise TypeMismatchError(
                        "Invalid type for data in filter:" + str(fltr)
                    )

                if fltr[1] == "is":
                    fltr_string = fltr[0] + "='" + fltr[2] + "'"

                elif fltr[1] == "is_not":
                    fltr_string = "NOT (" + fltr[0] + "='" + fltr[2] + "')"

                elif fltr[1] == "contains":
                    fltr_string = fltr[0] + " LIKE '%" + fltr[2] + "%'"

                elif fltr[1] == "does_not_contain":
                    fltr_string = "NOT (" + fltr[0] + " LIKE '%" + fltr[2] + "%')"

                else:
                    self.conn.close()
                    raise InvalidFilterError(
                        "Invalid Condition for filter:" + str(fltr)
                    )

            elif isinstance(fltr[2], int):
                # check if type is integer but acceptable type is string.
                if all_fields[fltr[0]] == "TEXT":
                    self.close_conn()
                    raise TypeMismatchError(
                        "Invalid type for data in filter:" + str(fltr)
                    )

                if fltr[1] == "less_than":
                    fltr_string = fltr[0] + "<" + str(fltr[2])

                elif fltr[1] == "less_than_equal":
                    fltr_string = fltr[0] + "<=" + str(fltr[2])

                elif fltr[1] == "greater_than":
                    fltr_string = fltr[0] + ">" + str(fltr[2])

                elif fltr[1] == "greater_than_equal":
                    fltr_string = fltr[0] + ">=" + str(fltr[2])

                elif fltr[1] == "equals":
                    fltr_string = fltr[0] + "=" + str(fltr[2])

                elif fltr[1] == "not_equal":
                    fltr_string = fltr[0] + "!=" + str(fltr[2])

                else:
                    self.conn.close()
                    raise InvalidFilterError(
                        "Invalid Condition for filter:" + str(fltr)
                    )

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
            print("Database Operation Failed:", sql_command)
            return False

        for row in rows:
            data_dict = {}
            for index in range(len(fields)):
                data_dict[fields[index]] = row[index]

            return_data.append(data_dict)

        return return_data

    def update(self, table_name, _id, data):
        """Update existing data in specified table. Ignores wrong fields.

        Args:
            table_name (string): Table Name.
            _id (int): id of the record.
            data (dict): New Data record.

        Returns:
            bool: True if Successful. False if not.

        """
        update_data_str = ""
        all_fields = self.get_table_fields(table_name)

        for key, val in data.items():
            if key not in all_fields.keys():
                continue

            if key == "id":
                self.close_conn()
                raise IDError("ID field is Immutable and cannot be edited by user.")

            if isinstance(val, str):
                # check if type is string but acceptable type is integer.
                if all_fields[key] == "INTEGER":
                    self.close_conn()
                    raise TypeMismatchError("Invalid data type for:" + key + ":" + val)

                update_data_str += key + "='" + val + "', "

            elif isinstance(val, int):
                # check if type is integer but acceptable type is string.
                if all_fields[key] == "TEXT":
                    self.close_conn()
                    raise TypeMismatchError("Invalid data type for:" + key + ":" + val)

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
            self.close_conn()
            return False

    def delete(self, table_name, _id):
        """Delete data record based on specified id.

        Args:
            table_name (string): Table Name.
            _id (int): id of the record.

        Returns:
            bool: True if Successful. False if not.
        """
        sql_command = "DELETE FROM " + table_name + " WHERE id=" + str(_id) + ";"

        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close_conn()
            return False

    def get_table_fields(self, table_name):
        """Get all fields of specified table name.

        Args:
            table_name (string): Table Name.

        Returns:
            dict: Dictionary where key is field name and value is data_type
        """
        sql_command = "PRAGMA TABLE_INFO(" + table_name + ");"
        try:
            data = self.conn.execute(sql_command)
        except:
            print("Database Operation Failed:", sql_command)
            return False

        field_dict = {}
        for d in data.fetchall():
            field_dict[d[1]] = d[2]

        return field_dict

    def clear_all_data(self, table_name):
        """Clears all data in the specified table.

        Args:
            table_name (string): Table Name

        Returns:
            bool: True if Successful. False if not.
        """
        sql_command = "DELETE FROM " + table_name + ";"
        try:
            self.conn.execute(sql_command)
            self.conn.commit()
            return True
        except:
            self.close_conn()
            return False

    def close_conn(self):
        """Closes Connection."""
        self.conn.close()
