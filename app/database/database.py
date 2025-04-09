import MySQLdb as mdb
import sys

# Подключение к базе данных
try:
    db = mdb.connect(
        host="192.168.31.205",
        port=3306,
        user="root",
        password="root",
        database="pyqt_mdk_11"
    )
except mdb.Error as e:
    print("Ошибка подключения к базе данных:", e)
    sys.exit(1)


class DB:
    # Staff
    @classmethod
    def get_staff(cls):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM staff"
                )
                staff = cursor.fetchall()
            return staff
        except mdb.Error as e:
            print("Ошибка получения сотрудников:", e)
            return []

    @classmethod
    def get_staffer_benefits(cls, staff_id: int):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT staff.is_veteran, "
                    "EXISTS (SELECT 1 FROM children "
                    "WHERE children.staff_id = staff.id) "
                    "FROM staff "
                    "WHERE staff.id = %s",
                    (staff_id,)
                )
                befits = cursor.fetchall()
            return befits
        except mdb.Error as e:
            print("Ошибка получения льгот сотрудника:", e)
            return []


    @classmethod
    def get_type_operation(cls):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM type_operation"
                )
                types_operation = cursor.fetchall()
            return types_operation
        except mdb.Error as e:
            print("Ошибка получения типов операций:", e)
            return []

    @classmethod
    def calculate_result(cls, staff_id: int, tax_base: bool, ndfl: bool, veteran: bool, children: bool):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT calculate_tax(%s, %s, %s, %s, %s)",
                    (staff_id, tax_base, ndfl, veteran, children)
                )
                result = cursor.fetchone()
            return result
        except mdb.Error as e:
            print("Ошибка получения расчёта:", e)
            return None

    @classmethod
    def record_result(cls, staff_id: int, tax_base: bool, ndfl: bool, veteran: bool, children: bool):
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT record_tax(%s, %s, %s, %s, %s)",
                    (staff_id, tax_base, ndfl, veteran, children)
                )
                db.commit()
                result = cursor.fetchone()
                del result
            return "Запись произведена"
        except mdb.Error as e:
            print("Ошибка записи:", e)
            return None
