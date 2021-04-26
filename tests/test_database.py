from app.database import *
from unittest import mock, TestCase
import MySQLdb

DB = ""
HOST = "localhost"
USER = "root"
PASSWORD = ""
PORT = 3306


class TestDataBase(TestCase):

    @mock.patch("app.database.MySQLdb")
    def test_create_connection_and_cursor_works(self, mock_mysql):
        mock_mysql.connect.return_value = MySQLdb.connect(host=HOST, user=USER, port=PORT)

        DataBase().create_connection_and_cursor()
        mock_mysql.connect.assert_called_once()

    def test_conn_and_cursor_exist(self):
        self.assertFalse(DataBase().conn_and_cursor_exist())

        with mock.patch("app.database.DataBase.cursor", create=True) as mock_cursor:
            with mock.patch("app.database.DataBase.conn", create=True) as mock_conn:
                self.assertTrue(DataBase().conn_and_cursor_exist())

    def test_is_database_selected(self):
        with mock.patch("app.database.DataBase.cursor", create=True) as mock_cursor:
            mock_cursor.execute.return_value = None
            self.assertTrue(DataBase().is_database_selected())

        self.assertFalse(DataBase().is_database_selected())

    @mock.patch("app.database.DataBase.conn", create=True)
    def test_change_current_database_works(self, mock_conn):
        mock_conn.select_db.return_value = None
        DataBase().change_current_database("")

    def test_convert_list_to_sql_string_works(self):
        list_to_test = ["default", 0, 0.5, "Gustavo", "2021-05-02"]

        result = DataBase().convert_list_to_sql_string(list_to_test)
        self.assertEqual(result, "default,0,0.5,'Gustavo','2021-05-02'")

    @mock.patch("app.database.DataBase.is_database_selected")
    @mock.patch("app.database.DataBase.conn_and_cursor_exist")
    def test_verify_database_requirements_works(self, mock_conn_and_cursor_exist, mock_is_database_selected):
        mock_conn_and_cursor_exist.return_value = False
        with self.assertRaises(Exception) as error:
            DataBase().insert_data("", [])

        self.assertEqual("Connetion or cursor is not defined!", error.exception.args[0])

        mock_conn_and_cursor_exist.return_value = True

        # ///////////////////////////////////////////////////////////////////////////

        mock_is_database_selected.return_value = False
        with self.assertRaises(Exception) as error:
            DataBase().insert_data("", [])

        self.assertEqual("Database is not selected!", error.exception.args[0])

        mock_is_database_selected.return_value = True

    @mock.patch("app.database.DataBase.verify_database_requirements")
    @mock.patch("app.database.DataBase.is_database_selected")
    @mock.patch("app.database.DataBase.conn_and_cursor_exist")
    def test_insert_data_works(self, mock_conn_and_cursor_exist, mock_is_database_selected,
                               mock_verify_database_requirements):

        with mock.patch("app.database.DataBase.cursor", create=True) as mock_cursor:
            mock_cursor.execute.side_effect = [0, 1]
            mock_verify_database_requirements.return_value = True
            self.assertFalse(DataBase().insert_data("", []))
            self.assertTrue(DataBase().insert_data("", []))

        self.assertFalse(DataBase().insert_data("", []))

    @mock.patch("app.database.DataBase.verify_database_requirements")
    def test_update_data_works(self, mock_verify_database_requirements):
        with mock.patch("app.database.DataBase.cursor", create=True) as mock_cursor:
            mock_verify_database_requirements.return_value = True
            self.assertFalse(DataBase().update_data("", dict(teste="tested"), dict()))
            self.assertFalse(DataBase().update_data("", dict(teste="tested"), dict(teste="tested")))
            self.assertFalse(DataBase().update_data("", dict(teste=1), dict(teste=1)))
            self.assertFalse(DataBase().update_data("", dict(teste=1.0), dict(teste=1.0)))
            self.assertFalse(DataBase().update_data("", dict(), dict(teste=1.0)))
            mock_cursor.execute.return_value = True
            self.assertTrue(DataBase().update_data("", dict(teste="tested"), dict(teste=1.0)))


    @mock.patch("app.database.DataBase.verify_database_requirements")
    def test_get_data_works(self, mock_verify_database_requirements):
        with mock.patch("app.database.DataBase.cursor", create=True) as mock_cursor:
            with mock.patch("app.database.DataBase.cursor.fetchall", create=True) as mock_fetchall:
                mock_verify_database_requirements.return_value = True
                mock_cursor.execute.side_effect = [0, 0, 1, 1, 1]
                mock_fetchall.return_value = [dict(teste="tested")]
                self.assertEqual(DataBase().get_data("", dict(teste="tested")), [dict(teste="tested")])
                self.assertEqual(DataBase().get_data("", dict()), [dict(teste="tested")])
                self.assertEqual(DataBase().get_data("", dict(teste=1.0)), [dict(teste="tested")])
                self.assertEqual(DataBase().get_data("", dict(teste=1)), [dict(teste="tested")])
            self.assertEqual(DataBase().get_data("", dict(teste="tested")), [])

    @mock.patch("app.database.DataBase.verify_database_requirements")
    def test_delete_data_works(self, mock_verify_database_requirements):
        with mock.patch("app.database.DataBase.cursor", create=True) as mock_cursor:
            mock_verify_database_requirements.return_value = True
            self.assertFalse(DataBase().delete_data("", dict()))
            self.assertTrue(DataBase().delete_data("", dict(teste="tested")))
        self.assertFalse(DataBase().delete_data("", dict(teste="tested")))
