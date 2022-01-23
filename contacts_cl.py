import os
import re
import sys
import argparse
from pprint import pprint
from include.contacts_db import ContactsDB

class ContactsCL(object):
    def __init__(self):
        home_path = os.path.expanduser("~")
        db_path = home_path + "/contacts_db/contacts.db"
        self.contacts_db = ContactsDB(db_path)

    def create_table(self, table_name):
        # builds table based on table_name
        print("\nPlease Enter the fields you need based on this convention:")
        print("<field_name_1>=><field_type>|<field_name_2>=><field_type>|...")
        column_str = input("Fields: ")
        columns_dict = {}

        for column in column_str.split("|"):
            column = column.strip()
            if len(column.split("=>")) != 2:
                self.contacts_db.close()
                raise Exception("Invalid Columns!")

            column_name, column_type = column.split("=>")
            columns_dict[column_name] = column_type

        result = self.contacts_db.create_table(table_name, columns_dict)
        if result:
            print("Table:", table_name, "successfully created.")

    def delete_table(self, table_name):
        result = self.contacts_db.delete_table(table_name)
        if result:
            print("Table:", table_name, "successfully removed.")

    def list_tables(self):
        result = self.contacts_db.list_tables()
        pprint(result)

    def add_data(self, table_name):
        print("\nPlease Enter the data you want to add based on this convention:")
        print("<field_name_1>=><data_1>|<field_name_2>=><data_2>|...")
        # TO DO: Write more instructions on how this will work
        data_str = input("Data: ")
        data = self._parse_data_str(data_str)

        result = self.contacts_db.add(table_name, data)
        if result:
            print("Data successfully added.")


    def find_data(self, table_name, display_style="dict"):
        print("\nPlease Enter the filter for your find based on this convention:")
        print("<field_name_1>~<operator>~<value>|<field_name_2>~<operator>~<value>|..")
        print("Valid Operators for Strings:")
        filter_str = input("Filter: ")
        filters = []
        for f in filter_str.split("|"):
            filter_parts = f.split("~")
            if len(filter_parts) != 3:
                self.contacts_db.close()
                raise Exception("Invalid Filter!")

            if not re.match("\".+\"", filter_parts[2]) and filter_parts[2].isnumeric():
                filters.append([filter_parts[0], filter_parts[1], int(filter_parts[2])])

            # check if data is a valid string
            elif re.match("\".+\"", filter_parts[2]) and not filter_parts[2].isnumeric():
                filters.append([filter_parts[0], filter_parts[1], filter_parts[2].strip("\"")])

            else:
                self.contacts_db.close()
                raise Exception("Invalid Filter!")

        print("\nPlease Enter the fields you want to display based on this convention:")
        print("<field_name_1>|<field_name_2>|..")
        fields_str = input("Fields: ")
        fields = [f for f in fields_str.split("|")]
        print(filters)
        result = self.contacts_db.find(table_name, filters, fields)
        if result:
            # TO DO: Support tabular and dictionary views
            if display_style == 'dict':
                pprint(result)
            elif display_style == 'tabular':
                self._display_tabular_dict(result)

    def delete_data(self, table_name):
        print("\nPlease Enter the ids to delete based on this convention:")
        print("<id_1>|<id_2>")
        id_str = input("IDs:")
        ids = [int(_id) for _id in id_str.split("|")]
        result = self.contacts_db.delete(table_name, ids)
        if result:
            print("Data successfully removed!")

    def update_data(self, table_name, _id):
        # Check if data exists before the prompt
        print("Please Enter the data you want to add based on this convention:")
        print("<field_name_1>=><data_1>|<field_name_2>=><data_2>|...")
        # TO DO: Write more instructions on how this will work
        data_str = input("Data: ")
        data = self._parse_data_str(data_str)
        result = self.contacts_db.update(table_name, _id, data)
        if result:
            print("Data successfully updated!")


    def list_data(self, table_name, display_style):
        result = self.contacts_db.find(table_name, [], [])
        if result:
            pprint(result)

    def _parse_data_str(self, data_str, ):
        data_dict = {}
        for data in data_str.split("|"):
            if not data:
                continue

            if len(data.split("=>")) != 2:
                self.contacts_db.close()
                raise Exception("Invalid Filter!")

            key, val = data.split("=>")
            # check if data is an integer
            if not re.match("\".+\"", val) and val.isnumeric():
                data_dict[key] = int(val)

            # check if data is a valid string
            elif re.match("\".+\"", val) and not val.isnumeric():
                data_dict[key] = val.strip("\"")

            else:
                raise Exception("Unsupported Data!")

        return data_dict

    def _display_tabular_dict(self, data_dict_list):
        keys = list(data_dict_list[0].keys())
        header_str = ""
        for key in keys:
            header_str += "|{:<20}".format(key.rjust(10))
        header_str += "|"

        print(header_str)
        for data_dict in data_dict_list:
            data_str = ""
            for k, v in data_dict.items():
                data_str += "|{:<20}".format(str(v).rjust(10))

            data_str += "|"
            print(data_str)

def main():
    contacts_cl = ContactsCL()
    return contacts_cl


if __name__ == "__main__":
    contacts_cl = main()
    parser = argparse.ArgumentParser()
    parser.add_argument("--create_table", help="Set this to build a new table.", action="store_true")
    parser.add_argument("--delete_table", help="Set this to remove the table from the database.", action="store_true")
    parser.add_argument("--list_tables", help="Set this to display all tables in the database.", action="store_true")
    parser.add_argument("--add_data", help="Set this to add data to specified table name.", action="store_true")
    parser.add_argument("--find_data", help="Set this to find data in specified table name.", action="store_true")
    parser.add_argument("--delete_data", help="Set this to remove data to specified table name based on the provided id.", action="store_true")
    parser.add_argument("--update_data", help="Set this to update data to specified table name based on the provided id.", action="store_true")
    parser.add_argument("--list_data", help="Show all data in specified table name.", action="store_true")

    parser.add_argument("--table_name", help="Table name to perform the operation on.", type=str)
    parser.add_argument("--id", help="ID of the record you want to remove or update", type=int)
    parser.add_argument("--display_style", help="Set this to display find data in a specific order. Supported modes are: \"dict\" and \"tabular\"", type=str)

    args = parser.parse_args()
    if args.create_table:
        contacts_cl.create_table(args.table_name)

    elif args.delete_table:
        contacts_cl.delete_table(args.table_name)

    elif args.list_tables:
        contacts_cl.list_tables()

    elif args.add_data:
        contacts_cl.add_data(args.table_name)

    elif args.find_data:
        contacts_cl.find_data(args.table_name, args.display_style)

    elif args.delete_data:
        contacts_cl.delete_data(args.table_name)

    elif args.update_data:
        contacts_cl.update_data(args.table_name, args.id)

    elif args.list_data:
        contacts_cl.list_data(args.table_name, args.display_style)

