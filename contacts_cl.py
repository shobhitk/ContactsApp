"""Contacts Commandline Code.

Author: Shobhit Khinvasara
"""
import os
import re
import sys
import argparse
from pprint import pprint
from include.contacts_db import ContactsDB

class ContactsCL(object):

    """Contacts CommandLine interface implementation.

    Attributes:
        contacts_db (ContactsDB): Contacts Database Connection Object.
    """

    def __init__(self):
        """Initialization Function for Contacts Commandline Application Class."""
        home_path = os.path.expanduser("~")
        db_path = home_path + "/contacts_db/contacts.db"
        self.contacts_db = ContactsDB(db_path)

    def create_table(self, table_name):
        """Create Table in the database.

        Args:
            table_name (str): Table Name.
        """
        if self.contacts_db.does_table_exist(table_name):
            print("Table Already Exists. Aborting..")
            self.contacts_db.close_conn()
            return

        if not re.match("^[a-zA-Z0-9_]+$", table_name):
            print("Invalid or Unsupported table name. Aborting..")
            self.contacts_db.close_conn()
            return

        print("\nPlease Enter the fields you need based on this convention:")
        print("<field_name_1>=><field_type>|<field_name_2>=><field_type>|...")
        field_str = input("Fields: ")
        fields_dict = {}

        for field in field_str.split("|"):
            field = field.strip()
            if len(field.split("=>")) != 2:
                print("Invalid Fields!")
                self.contacts_db.close_conn()
                return

            field_name, field_type = field.split("=>")
            fields_dict[field_name] = field_type

        result = self.contacts_db.create_table(table_name, fields_dict)
        if result:
            print("Table:", table_name, "successfully created.")

        self.contacts_db.close_conn()
        return

    def delete_table(self, table_name):
        """Delete Table from the database.

        Args:
            table_name (str): Table Name.
        """
        if not self.contacts_db.does_table_exist(table_name):
            print("Table doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        result = self.contacts_db.delete_table(table_name)
        if result:
            print("Table:", table_name, "successfully removed.")

        self.contacts_db.close_conn()
        return

    def list_tables(self):
        """Display all Tables in the Database."""
        result = self.contacts_db.list_tables()
        result = [r for r in result if r != "sqlite_sequence"]
        print(result)
        self.contacts_db.close_conn()
        return

    def display_table_schema(self, table_name):
        """Display Table Schema i.e. field_name:data_type

        Args:
            table_name (string): Table Name.
        """
        if not self.contacts_db.does_table_exist(table_name):
            print("Table doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        result = self.contacts_db.get_table_fields(table_name)
        pprint(result)
        self.contacts_db.close_conn()
        return

    def add_data(self, table_name):
        """Add Record in the Table.

        Args:
            table_name (string): Table Name.
        """
        if not self.contacts_db.does_table_exist(table_name):
            print("Table doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        print("\nPlease Enter the data you want to add based on this convention:")
        print("<field_name_1>=><data_1>|<field_name_2>=><data_2>|...")
        print(
            'Please enclose text data in ("). Integer data should be specified as it is.'
        )
        data_str = input("Data: ")
        data = self._parse_data_str(data_str)
        if not data:
            self.contacts_db.close_conn()
            return

        result = self.contacts_db.add(table_name, data)
        if result:
            print("Data successfully added.")

        self.contacts_db.close_conn()
        return

    def find_data(self, table_name, display_style="dict"):
        """Find Record in the Table.

        Args:
            table_name (string): Table Name.
            display_style (str, optional): Display Style.
                Supported Values are "dict" and "tabular".
        """
        if not self.contacts_db.does_table_exist(table_name):
            print("Table doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        print("\nPlease Enter the filter for your find based on this convention:")
        print("<field_name_1>~<operator>~<value>|<field_name_2>~<operator>~<value>|..")
        print("Valid Operators for Strings: is, is_not, contains, does_not_contain.")
        print(
            "Valid Operators for Integers: less_than, less_than_equal, greater_than, greater_than_equal, equals, not_equal."
        )
        print(
            'Please enclose text value in ("). Integer value should be specified as it is.'
        )
        filter_str = input("Filter: ")
        filters = []
        for f in filter_str.split("|"):
            filter_parts = f.split("~")
            if len(filter_parts) != 3:
                print("Invalid Filter!")
                self.contacts_db.close_conn()
                return

            if not re.match('".+"', filter_parts[2]) and filter_parts[2].isnumeric():
                filters.append(
                    [filter_parts[0], filter_parts[1], int(filter_parts[2])]
                )

            # check if data is a string is enclosed in quotes.
            elif re.match('".+"', filter_parts[2]) and not filter_parts[2].isnumeric():
                filters.append(
                    [filter_parts[0], filter_parts[1], filter_parts[2].strip('"')]
                )

            else:
                print("Invalid Filter!")
                self.contacts_db.close_conn()
                return

        print("\nPlease Enter the fields you want to display based on this convention:")
        print("<field_name_1>|<field_name_2>|..")
        fields_str = input("Fields: ")
        fields = [f for f in fields_str.split("|")]
        result = self.contacts_db.find(table_name, filters, fields)
        if result:
            if display_style == "dict":
                pprint(result)
            elif display_style == "tabular":
                self._display_tabular_dict(result)
            else:
                print("Unsupported or Missing display style. Aborting..")

        self.contacts_db.close_conn()
        return

    def delete_data(self, table_name, _id):
        """Delete Record from the Table.

        Args:
            table_name (string): Table Name.
            _id (int): ID of the record.
        """
        if not self.contacts_db.does_table_exist(table_name):
            print("Table doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        if not self.contacts_db.find_data(table_name, [["id", "equals", _id]]):
            print("Record doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        result = self.contacts_db.delete(table_name, _id)
        if result:
            print("Data successfully removed!")

        self.contacts_db.close_conn()
        return

    def update_data(self, table_name, _id):
        """Update Record in the Table.

        Args:
            table_name (string): Table Name.
            _id (int): ID of the record.
        """
        if not self.contacts_db.does_table_exist(table_name):
            print("Table doesn't exist. Aborting..")
            return

        if not self.contacts_db.find_data(table_name, [["id", "equals", _id]]):
            print("Record doesn't exist. Aborting..")
            self.contacts_db.close_conn()
            return

        print("Please Enter the data you want to add based on this convention:")
        print("<field_name_1>=><data_1>|<field_name_2>=><data_2>|...")
        print(
            'Please enclose text data in ("). Integer data should be specified as it is.'
        )
        data_str = input("Data: ")
        data = self._parse_data_str(data_str)
        if not data:
            self.contacts_db.close_conn()
            return

        result = self.contacts_db.update(table_name, _id, data)
        if result:
            print("Data successfully updated!")

        self.contacts_db.close_conn()
        return

    def list_data(self, table_name, display_style="dict"):
        """Summary

        Args:
            table_name (string): Table Name.
            display_style (str, optional): Display Style.
                Supported Values are "dict" and "tabular".
        """
        result = self.contacts_db.find(table_name, [], [])
        if result:
            if display_style == "dict":
                pprint(result)
            elif display_style == "tabular":
                self._display_tabular_dict(result)
            else:
                print("Unsupported or Missing display style. Aborting..")

        self.contacts_db.close_conn()
        return

    def _parse_data_str(self, data_str):
        """Helper Function to parse input data string and convert them into a usable dictionary.

        Args:
            data_str (string): data_string to parse.
        """
        data_dict = {}
        for data in data_str.split("|"):
            if not data:
                continue

            if len(data.split("=>")) != 2:
                print("Invalid Filter!")
                return False

            key, val = data.split("=>")
            # check if data is an integer
            if not re.match('".+"', val) and val.isnumeric():
                data_dict[key] = int(val)

            # check if data is a valid string
            elif re.match('".+"', val) and not val.isnumeric():
                data_dict[key] = val.strip('"')

            else:
                print("Unsupported Data!")
                return False

        return data_dict

    def _display_tabular_dict(self, data_dict_list):
        """Helper Function to display a dict list in tabular form.

        Args:
            data_dict_list (list): List of Dictionaries
        """
        keys = list(data_dict_list[0].keys())
        header_str = ""
        for key in keys:
            header_str += "|{:<40}".format(key.rjust(20))
        header_str += "|"

        print(header_str)
        for data_dict in data_dict_list:
            data_str = ""
            for k, v in data_dict.items():
                data_str += "|{:<40}".format(str(v).rjust(20))

            data_str += "|"
            print(data_str)


def main():
    """Main Function

    Returns:
        object: Contacts CommandLine Instance
    """
    contacts_cl = ContactsCL()
    return contacts_cl


if __name__ == "__main__":
    contacts_cl = main()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--create_table", help="Set this to build a new table.", action="store_true"
    )
    parser.add_argument(
        "--delete_table",
        help="Set this to remove the table from the database.",
        action="store_true",
    )
    parser.add_argument(
        "--list_tables",
        help="Set this to display all tables in the database.",
        action="store_true",
    )
    parser.add_argument(
        "--display_table_schema",
        help="Set this to display table schema i.e. name of fields and their type.",
        action="store_true",
    )
    parser.add_argument(
        "--add_data",
        help="Set this to add data to specified table name.",
        action="store_true",
    )
    parser.add_argument(
        "--find_data",
        help="Set this to find data in specified table name.",
        action="store_true",
    )
    parser.add_argument(
        "--delete_data",
        help="Set this to remove data to specified table name based on the provided id.",
        action="store_true",
    )
    parser.add_argument(
        "--update_data",
        help="Set this to update data to specified table name based on the provided id.",
        action="store_true",
    )
    parser.add_argument(
        "--list_data",
        help="Show all data in specified table name.",
        action="store_true",
    )

    parser.add_argument(
        "--table_name", help="Table name to perform the operation on.", type=str
    )
    parser.add_argument(
        "--id", help="ID of the record you want to remove or update", type=int
    )
    parser.add_argument(
        "--display_style",
        help='Set this to display find data in a specific order. Supported modes are: "dict" and "tabular"',
        type=str,
    )

    args = parser.parse_args()
    if args.create_table:
        contacts_cl.create_table(args.table_name)

    elif args.delete_table:
        contacts_cl.delete_table(args.table_name)

    elif args.list_tables:
        contacts_cl.list_tables()

    elif args.display_table_schema:
        contacts_cl.display_table_schema(args.table_name)

    elif args.add_data:
        contacts_cl.add_data(args.table_name)

    elif args.find_data:
        contacts_cl.find_data(args.table_name, args.display_style)

    elif args.delete_data:
        contacts_cl.delete_data(args.table_name, args._id)

    elif args.update_data:
        contacts_cl.update_data(args.table_name, args.id)

    elif args.list_data:
        contacts_cl.list_data(args.table_name, args.display_style)
