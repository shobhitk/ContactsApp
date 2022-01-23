import unittest
from contacts_db import ContactsDB

unittest.TestLoader.sortTestMethodsUsing = None

class TestContactsDb(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.contacts_db = ContactsDB(":memory:")

	def test_1_create_table(self):
		self.contacts_db.create_table("Test_Table",{"name":"text","age":"int"})
		tables = self.contacts_db.list_tables()
		self.assertEqual("Test_Table" in tables, True)

	def test_2_delete_table(self):
		self.contacts_db.create_table("Bad_Table",{"name":"text","age":"text"})
		self.contacts_db.delete_table("Bad_Table")
		tables = self.contacts_db.list_tables()
		self.assertEqual("Bad_Table" in tables, False)

	def test_3_add_data(self):
		result = self.contacts_db.add("Test_Table", {"name":"ABC","age":24})
		self.assertEqual(result, True)

	def test_4_find_data(self):
		result = self.contacts_db.find("Test_Table", [["age","equals",24]], ["id","name"])
		self.assertEqual(result[0], {"id":1,"name":"ABC"})

	def test_5_update_data(self):
		self.contacts_db.update("Test_Table", 1, {"age":25})
		result = self.contacts_db.find("Test_Table", [["age","equals",25]], ["id","name"])
		self.assertEqual(result[0], {"id":1,"name":"ABC"})

	def test_6_delete_data(self):
		self.contacts_db.add("Test_Table", {"name":"DEF","age":10})
		self.contacts_db.delete("Test_Table", [2])
		result = self.contacts_db.find("Test_Table", [["id","equals",2]], ["id","name"])
		self.assertEqual(result, [])

	def test_7_clear_data(self):
		self.contacts_db.clear_all_data("Test_Table")
		result = self.contacts_db.find("Test_Table", [], ["id","name"])
		self.assertEqual(result, [])

	@classmethod
	def tearDownClass(self):
		self.contacts_db.close()
		print('tearDown called!')


if __name__ == '__main__':
	unittest.main()
