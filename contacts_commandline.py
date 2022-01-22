# Command Line tool for Contacts Management
# Initialize Database
# 	python -init path
# Build Table
#	python -create_table <table_name>
# 	>>fields: name:text, address:text, phone_number:text,
# Remove Table
#	python -remove_table <table_name>
# Add Data
#	python -add_data <table_name>
#	>> values: name:"Shobhit Khinvasara",address:"1130, 240 St", phone_number:"236-688-6126"
# Get Data
#	python -find <table_name> -display_style dict -fields name,phone_number
# 	filter: name is "Shobhit Khinvasara",phone_number contains "236"
# 	return:
# 	id:2,
# 	name: Shobhit Khinvasara
# 	phone_number: 236-688-6126
# Remove Data
# 	python -remove <table_name> -id 2
# Update Data
# 	python -update <table_name> -id 2
#	>> values: name "Shobhit Khinvasara", address "1130, 240 St", phone_number "236-688-4650"

