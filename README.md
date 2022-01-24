This is a Contacts Commandline Application using SQLite3 Python Module to store and manage a persistant database.
This application allows the following features:

1. Creating tables.
2. Deleting table.
3. Listing all tables.
4. Show Table Info.
5. Add Data in table.
6. Search and Find data in table.
7. Removing Data in table.
8. Updating Data in Table
9. Displaying all data in table in JSON dictionary or tabular format.

Requires Python3.

CommandLine Tool Usage:
>> python <path_to_tool>\contacts_cl.py -h
usage: contacts_cl.py [-h] [--create_table] [--delete_table] [--list_tables] [--display_table_schema] [--add_data] [--find_data] [--delete_data] [--update_data] [--list_data] [--table_name TABLE_NAME] [--id ID]
                      [--display_style DISPLAY_STYLE]

optional arguments:
  -h, --help            show this help message and exit
  --create_table        Set this to build a new table.
  --delete_table        Set this to remove the table from the database.
  --list_tables         Set this to display all tables in the database.
  --display_table_schema
                        Set this to display table schema i.e. name of fields and their type.
  --add_data            Set this to add data to specified table name.
  --find_data           Set this to find data in specified table name.
  --delete_data         Set this to remove data to specified table name based on the provided id.
  --update_data         Set this to update data to specified table name based on the provided id.
  --list_data           Show all data in specified table name.
  --table_name TABLE_NAME
                        Table name to perform the operation on.
  --id ID               ID of the record you want to remove or update
  --display_style DISPLAY_STYLE
                        Set this to display find data in a specific order. Supported modes are: "dict" and "tabular"


EXAMPLE USAGE:
Create Table:
>>python <path_to_tool>\contacts_cl.py --create_table --table_name Test_Table

Please Enter the fields you need based on this convention:
<field_name_1>=><field_type>|<field_name_2>=><field_type>|...
Fields: name=>text|school_id=>integer
Table: Test_Table successfully created.

Add Data to Table:
>>python <path_to_tool>\contacts_cl.py --add_data --table_name New_Contacts

Please Enter the data you want to add based on this convention:
<field_name_1>=><data_1>|<field_name_2>=><data_2>|...
Data: name=>"Joy"|age=>26
Data successfully added.


