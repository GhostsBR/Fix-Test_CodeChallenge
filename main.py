from app import database
db = database.DataBase()
db.create_connection_and_cursor("proway")

print(db.get_data("hotels", dict(name="sacolao")))