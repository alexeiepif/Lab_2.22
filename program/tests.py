import sqlite3
import unittest
from pathlib import Path

from program.ind import add_route, create_db, select_all, select_routes

# Для индивидуального задания лабораторной работы 2.21 добавьте
# тесты с использованием модуля unittest,
# проверяющие операции по работе с базой данных.


class TestCreateDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test.db")

    def tearDown(self):
        self.test_dir.unlink(missing_ok=True)

    def test_create_database(self):
        TestRoutes.not_skip = False
        create_db(self.test_dir)
        self.assertTrue(self.test_dir.exists())

        conn = sqlite3.connect(self.test_dir)
        cursor = conn.cursor()

        # Проверка наличия таблицы 'start'
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='start';"
        )
        self.assertTrue(cursor.fetchone())

        # Проверка структуры таблицы 'start'
        cursor.execute("PRAGMA table_info(start);")
        columns = cursor.fetchall()
        expected_columns = [
            (0, "start_id", "INTEGER", 0, None, 1),
            (1, "start_point", "TEXT", 1, None, 0),
        ]
        self.assertEqual(columns, expected_columns)

        # Проверка наличия таблицы 'routes'
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='routes';"
        )
        self.assertTrue(cursor.fetchone())

        # Проверка структуры таблицы 'routes'
        cursor.execute("PRAGMA table_info(routes);")
        columns = cursor.fetchall()
        expected_columns = [
            (0, "start_id", "INTEGER", 1, None, 0),
            (1, "route_number", "INTEGER", 0, None, 1),
            (2, "end_point", "TEXT", 1, None, 0),
        ]
        self.assertEqual(columns, expected_columns)

        conn.close()

        TestRoutes.not_skip = True


class TestRoutes(unittest.TestCase):
    not_skip = True

    @classmethod
    def setUpClass(self):
        # Пропускаем этот класс, если предыдущий класс
        # тестирования завершился неудачно
        if self.not_skip:
            pass
        else:
            raise unittest.SkipTest("create_db fail")

    def setUp(self):
        self.db_path = Path("test.db")
        create_db(self.db_path)

    def tearDown(self):
        self.db_path.unlink(missing_ok=True)

    def test_add_route(self):
        add_route(self.db_path, "A", "B", 1)
        add_route(self.db_path, "C", "D", 2)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM start")
        self.assertEqual(cursor.fetchone()[0], 2)

        cursor.execute("SELECT COUNT(*) FROM routes")
        self.assertEqual(cursor.fetchone()[0], 2)

        cursor.execute(
            """
            SELECT start.start_point, routes.end_point, routes.route_number
            FROM start
            INNER JOIN routes ON routes.start_id = start.start_id
            """
        )
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertDictEqual(
            {
                "начальный пункт": rows[0][0],
                "конечный пункт": rows[0][1],
                "номер маршрута": rows[0][2],
            },
            {
                "начальный пункт": "a",
                "конечный пункт": "b",
                "номер маршрута": 1,
            },
        )
        self.assertDictEqual(
            {
                "начальный пункт": rows[1][0],
                "конечный пункт": rows[1][1],
                "номер маршрута": rows[1][2],
            },
            {
                "начальный пункт": "c",
                "конечный пункт": "d",
                "номер маршрута": 2,
            },
        )

        conn.close()

    def test_select_all(self):
        add_route(self.db_path, "A", "B", 1)
        add_route(self.db_path, "C", "D", 2)

        routes = select_all(self.db_path)
        self.assertEqual(len(routes), 2)
        self.assertDictEqual(
            routes[0],
            {
                "начальный пункт": "a",
                "конечный пункт": "b",
                "номер маршрута": 1,
            },
        )
        self.assertDictEqual(
            routes[1],
            {
                "начальный пункт": "c",
                "конечный пункт": "d",
                "номер маршрута": 2,
            },
        )

    def test_select_routes(self):
        add_route(self.db_path, "A", "B", 1)
        add_route(self.db_path, "C", "D", 2)
        add_route(self.db_path, "B", "C", 3)

        routes = select_routes(self.db_path, "B")
        self.assertEqual(len(routes), 2)
        self.assertDictEqual(
            routes[0],
            {
                "начальный пункт": "a",
                "конечный пункт": "b",
                "номер маршрута": 1,
            },
        )
        self.assertDictEqual(
            routes[1],
            {
                "начальный пункт": "b",
                "конечный пункт": "c",
                "номер маршрута": 3,
            },
        )


if __name__ == "__main__":
    unittest.main()
