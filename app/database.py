import MySQLdb

DB = ""
HOST = "localhost"
USER = "root"
PASSWORD = ""
PORT = 3306


class DataBase:

    def create_connection_and_cursor(self, db_name: str = "") -> None:
        self.conn = MySQLdb.connect(host=HOST, user=USER, password=PASSWORD, port=PORT, db=db_name)
        self.conn.autocommit(True)
        self.cursor = self.conn.cursor()

    def conn_and_cursor_exist(self) -> bool:
        try:
            self.conn
            self.cursor
            return True
        except AttributeError:
            return False

    def is_database_selected(self) -> bool:
        try:
            self.cursor.execute("CREATE TABLE temp_table (teste varchar(1))")
            self.cursor.execute("DROP TABLE temp_table")
            return True
        except Exception:
            return False

    def change_current_database(self, new_database_name: str) -> None:
        self.conn.select_db(new_database_name)

    def convert_list_to_sql_string(self, data: list) -> str:
        converted_to_sql_data = [f"'{value}'"
                                 if isinstance(value, str) and value.upper() != "DEFAULT" and value.upper() != "NULL"
                                 else str(value)
                                 for value in data]
        string_values = ",".join(converted_to_sql_data)
        return string_values

    def convert_dict_to_sql_string(self, dict_items: dict) -> list:
        list = []
        for key, value in dict_items:
            if type(value) == str:
                list.append("`%s` = '%s'" % (key, value))
            elif type(value) == float:
                list.append("`%s` = %s" % (key, value))
            elif type(value) == int:
                value = float(value)
                list.append("`%s` = %s" % (key, value))
        return list

    def verify_database_requirements(self, data) -> bool:
        if not self.conn_and_cursor_exist():
            raise Exception("Connetion or cursor is not defined!")
        if not self.is_database_selected():
            raise Exception("Database is not selected!")
        if not isinstance(data, list):
            raise TypeError("Data is not a list!")
        return True

    def insert_data(self, table_to_insert: str, data: list) -> bool:
        self.verify_database_requirements(data)

        string_values = self.convert_list_to_sql_string(data)
        sql = f"""INSERT INTO {table_to_insert} VALUES ({string_values})"""

        try:
            affected_rows = self.cursor.execute(sql)
            if affected_rows > 0:
                return True
        except:
            return False

        return False

    def update_data(self, table_to_update: str, data: dict, find: dict) -> bool:
        self.verify_database_requirements(data)
        self.verify_database_requirements(find)
        if not find:
            return False
        find = " AND ".join(self.convert_dict_to_sql_string(find.items()))
        data = ", ".join(self.convert_dict_to_sql_string(data.items()))
        if data == "":
            return False
        sql = f"""UPDATE `{table_to_update}` SET {data} WHERE {find}"""
        try:
            affected_rows = self.cursor.execute(sql)
            if affected_rows > 0:
                return True
        except:
            return False

    def get_data(self, table_to_get: str, find: dict) -> list:
        self.verify_database_requirements(find)
        if find:
            find = " AND ".join(self.convert_dict_to_sql_string(find.items()))
        sql = ""
        if not find:
            sql = f"""SELECT * FROM `{table_to_get}`"""
        else:
            sql = f"""SELECT * FROM `{table_to_get}` WHERE {find}"""
        try:
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except:
            return []

    def delete_data(self, table_to_delete: str, find: dict) -> bool:
        self.verify_database_requirements(find)
        sql = ""
        if not find:
            return False
        else:
            find = " AND ".join(self.convert_dict_to_sql_string(find.items()))
            sql = f"""DELETE FROM `{table_to_delete}` WHERE {find}"""
        try:
            self.cursor.execute(sql)
            return True
        except:
            return False