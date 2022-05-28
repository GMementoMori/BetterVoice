import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_users(self, status = True):
        """Получаем всех юзеров бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users`").fetchall()

    def user_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, username, status = True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `status`, `username`) VALUES(?,?,?)", (user_id, status, username))

    def status_subscription(self, user_id):
        """Проверяем статус подписки в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT `status` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            for row in result:
                result = row[0]
            return result

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def tel_number_exists(self, user_id, tel):
        """Проверяем, есть ли уже номер телефона в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users_telephones` WHERE `value` = ? AND `user_id` = ?', (tel, user_id,)).fetchall()
            return bool(len(result))

    def add_tel_number(self, user_id, tel):
        """Добавляем номер телефона пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `users_telephones` (`user_id`, `value`) VALUES(?,?)", (user_id, tel))

    def update_tel_number(self, user_id, tel):
        """Обновляем номер телефона пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `users_telephones` SET `value` = ? WHERE `user_id` = ?", (tel, user_id))

    def add_all_filter(self, user_id):
        """Добавляем фильтр пользователя"""
        with self.connection:
            self.cursor.execute("INSERT INTO `user_filter_rooms` (`user_id`, `rooms_count_id`) VALUES(?, 0)", (user_id,))
            self.cursor.execute("INSERT INTO `user_filter_city` (`user_id`, `city_id`) VALUES(?, 0)", (user_id,))
            self.cursor.execute("INSERT INTO `user_filter_area` (`user_id`, `area_id`) VALUES(?, 0)", (user_id,))
            return self.cursor.execute("INSERT INTO `user_filter_capital` (`user_id`, `capital_id`) VALUES(?, 0)", (user_id,))

    def get_filters(self, filters_table, field='', value=''):
        """Получаем все фильтры из нужной таблицы"""
        with self.connection:
            if(field != '' and value != ''):
                resultRows = []
                result = self.cursor.execute("SELECT * FROM "+filters_table+" WHERE "+field+" = "+value).fetchall()
                for row in result:
                    resultRows.append(row[0])
                return resultRows

            return self.cursor.execute("SELECT * FROM "+filters_table).fetchall()

    def get_active_filters(self, filters_table, relation_table, user_id):
        """Получаем все активные фильтры из нужной таблицы"""
        resultRows = []
        with self.connection:
            result = self.cursor.execute("SELECT first.id FROM "+filters_table+" AS first INNER JOIN "+relation_table+" AS second ON(first.id = second.filter_id AND second.user_id = '"+str(user_id)+"')").fetchall()
            for row in result:
                resultRows.append(row[0])
            return resultRows

    def add_filter(self, user_id, filter_table_name, filter_id):
        """Добавляет фильтр пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO "+filter_table_name+" (`user_id`, `filter_id`) VALUES("+str(user_id)+", "+str(filter_id)+")")

    def remove_filter(self, user_id, filter_table_name, filter_id):
        """Удяляет фильтр пользователя"""
        with self.connection:
            return self.cursor.execute("DELETE FROM "+filter_table_name+" WHERE `filter_id` = "+str(filter_id)+" AND `user_id` = "+str(user_id))


    def get_all_active_filters(self, user_id):
        """Получаем все активные фильтры из нужных таблиц"""
        resultRooms = []
        resultAreas = []
        resultCapitals = []

        with self.connection:
            active_rooms = self.cursor.execute("SELECT first.value FROM rooms_count AS first INNER JOIN user_filter_rooms AS second ON(first.id = second.filter_id AND second.user_id = '"+str(user_id)+"')").fetchall()
            active_areas = self.cursor.execute("SELECT first.value FROM areas AS first INNER JOIN user_filter_area AS second ON(first.id = second.filter_id AND second.user_id = '"+str(user_id)+"')").fetchall()
            active_capitals = self.cursor.execute("SELECT first.value FROM capitals AS first INNER JOIN user_filter_capital AS second ON(first.id = second.filter_id AND second.user_id = '"+str(user_id)+"')").fetchall()

            for room in active_rooms:
                resultRooms.append(room[0])
            for area in active_areas:
                resultAreas.append(area[0])
            for capital in active_capitals:
                resultCapitals.append(capital[0])

        return {'rooms':resultRooms,'areas':resultAreas,'capitals':resultCapitals}

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()