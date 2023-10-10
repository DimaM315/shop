# 
# DROP TABLE tablename;
# SHOW DATABASES;
# USE shopDB; SHOW TABLES; SHOW TABLES FROM shopDB;

from vars import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from mysql.connector import connect, Error


class DBController:
	# класс отвечающий за взаимодействие бд. Основной класс который будет использовать приложение.

	__CONN = connect(
	        host=DB_HOST,
	        user=DB_USER,
	        password=DB_PASSWORD,
	        db=DB_NAME
	    ) # При окончании использования класса, нужно закрывать коннект.


	@staticmethod
	def get_cursor():
		# курсор для работы с запросами к БД. Предназначен для использования в конструкции with
		# для гарантии что поток закроется по окончании использования
		return DBController.__CONN.cursor()

	@staticmethod
	def db_commit():
		# По умолчанию коннектор MySQL не выполняет автоматическую фиксацию транзакций. 
		# В MySQL модификации, упомянутые в транзакции, происходят только тогда, когда мы используем в конце команду COMMIT. 
		# Чтобы внести изменения в таблицу, вызываем этот метод после каждой транзакции.
		DBController.__CONN.commit()


	@staticmethod
	def get_passhash_from_login(login:str)->tuple:
		with DBController.get_cursor() as cursor:
			cursor.execute("select password from users where login='"+login+"';")
			result = cursor.fetchone()
			return None if result == None else result[0]

	@staticmethod
	def get_role_from_login(login:str)->tuple:
		with DBController.get_cursor() as cursor:
			cursor.execute("select role from users where login='"+login+"';")
			result = cursor.fetchone()
			return None if result == None else result[0]

	@staticmethod
	def get_user_data_from_login(login:str)->tuple:
		with DBController.get_cursor() as cursor:
			cursor.execute("select * from users where login='"+login+"';")
			return cursor.fetchone()		

	@staticmethod
	def get_user_data_from_id(user_id:int)->tuple:
		with DBController.get_cursor() as cursor:
			cursor.execute("select * from users where id_user='"+str(user_id)+"';")
			return cursor.fetchone()


	@staticmethod
	def create_new_user(name:str, login:str, password:str, color_in_chat:str):
		with DBController.get_cursor() as cursor:
			sql = "insert into users(name, login, password, date_reged, role, color_in_chat) VALUES " + \
			f"('{name}', '{login}', '{password}', now(), 'user', '{color_in_chat}');"
			cursor.execute(sql)

	@staticmethod
	def get_all_messeges()->list:
		# Используем inner join для получения данных из связных таблиц. Получаем лист вида:
		# [ ( id_user | name  | message  | date_sent | color_in_chat),
		#   ...
		# ]
		with DBController.get_cursor() as cursor:
			cursor.execute("SELECT u.id_user, u.name, m.message, DATE_FORMAT(m.date_sent, '%H:%i %d.%m'), u.color_in_chat FROM users AS u INNER JOIN msg_storage AS m ON u.id_user=m.from_user_id;")
			return cursor.fetchall()


	@staticmethod
	def get_last_msg_id()->int:
		with DBController.get_cursor() as cursor:
			cursor.execute("select id_msg from msg_storage order by id_msg DESC limit 1;")
			return cursor.fetchone()[0]


	@staticmethod
	def get_last_n_msg(n:int)->list:
		# Заведомо известно что n не больше последнего msg_id.
		# Возвращаются данные вида:
		# [ (id_msg | from_user_id | message | date_sent | color_in_chat)
		#   ...
		# ]
		with DBController.get_cursor() as cursor:
			cursor.execute("SELECT u.id_user, u.name, m.message, DATE_FORMAT(m.date_sent, '%H:%i %d.%m'), u.color_in_chat FROM users AS u INNER JOIN msg_storage AS m ON u.id_user=m.from_user_id order by id_msg DESC limit "+str(n)+";")
			return cursor.fetchall()


	@staticmethod
	def send_msg(user_id:int, msg_text:str):
		with DBController.get_cursor() as cursor:
			sql = "insert into msg_storage(from_user_id, message, date_sent) VALUES " + \
			f"({user_id}, '{msg_text}', now());"
			print(sql)
			cursor.execute(sql)



class DBIniter:
	# Класс отвечающий за инициализацию/миграция бд. 
	
	create_db_sql = "CREATE DATABASE IF NOT EXISTS shopDB CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
	drop_db_sql = "DROP DATABASE IF EXISTS shopDB;"
	show_db_sql = "SHOW DATABASES;"
	
	create_user_table = """create table IF NOT EXISTS users (
			id_user int (10) AUTO_INCREMENT,
			name varchar(20) NOT NULL,
			login varchar(50) NOT NULL UNIQUE,
			password varchar(64) NOT NULL,
			date_reged datetime NOT NULL,
			role varchar(20) NOT NULL,
			PRIMARY KEY (id_user),
			FOREIGN KEY (role) REFERENCES roles (name)
			);"""
	create_role_table = """create table IF NOT EXISTS roles (name varchar(20) NOT NULL UNIQUE);"""

	create_msg_storage_table = """create table IF NOT EXISTS msg_storage (
			id_msg int(10) AUTO_INCREMENT,
			from_user_id int(10) NOT NULL,		
			message text NOT NULL,
			date_sent datetime NOT NULL,
			PRIMARY KEY (id_msg),
			FOREIGN KEY (from_user_id) REFERENCES users (id_user) 
			); """


	@staticmethod
	def create_app_database(cursor):
		# здесь считаем что база данных приложения уже создана

		# создаём таблицу ролей 
		cursor.execute(DBIniter.create_role_table)
		# создаём таблицу пользователей
		cursor.execute(DBIniter.create_user_table)
		# создаём таблицу для хранения сообщений
		cursor.execute(DBIniter.create_msg_storage_table)

		# Создаём записи в созданных талицах.
		DBIniter.create_roles(cursor)
		DBIniter.create_primary_users(cursor)
		DBIniter.create_first_msg(cursor)

		print("Инициализация базы данных выполнена!")


	@staticmethod
	def create_roles(cursor):
		# Создаём поля ролей, которые будут иметь авторизованные пользователи приложения.
		cursor.execute("insert into roles(name) VALUES ('user'),('admin');")

	@staticmethod
	def create_primary_users(cursor):
		# Создаём начальных пользователей приложения. user1 - пароль user1, admin1 - admin1
		cursor.execute("""insert into users(name, login, password, date_reged, role)
			VALUES 
			('Имя Фамилия', 'user1', '77d9d48d2ac6ca6fff103f5f87d3c05531349e8ba805ea88dbd76e266a9cd16f', now(), 'user'),
			('Name Surname', 'admin1', '750ac79b05b8246dfc4de67dd77f37c39da1b37114870766d5de886bc67d9c1c', now(), 'admin');""")

	@staticmethod
	def create_first_msg(cursor):
		# Добавляем тестовые сообщение, что бы таблица не была пустой.
		cursor.execute("""insert into msg_storage(from_user_id, message, date_sent)
			VALUES
			(1, 'Всем привет!', now()),
			(2, 'Тестовое сообщение.', now()),
			(1, 'Hello world! 123 Hello world! 123  Hello world! 123  Hello world! 123 ', now()),
			(2, 'create_first_msg create_first_msg create_first_msg', now()),
			(2, 'Пятое сообщение!!!!', now());""")

	
	@staticmethod
	def refresh_db(cursor):
		cursor.execute(DBIniter.drop_db_sql)
		print("Удаление базы данных выполнено!")
		DBIniter.create_app_database(cursor)



def test1():
	try:
		with DBController.get_cursor() as cursor:
			print(cursor)
			DBIniter.create_app_database(cursor)
			print(cursor)

			#cursor.execute(DBIniter.show_db_sql)
			#result = cursor.fetchall()
			#for row in result:
			#	print(row)
	except Error as e:
		print(e)

	DBController.db_commit()

def test2():
	print(DBController.get_passhash_from_login("user1") == "77d9d48d2ac6ca6fff103f5f87d3c05531349e8ba805ea88dbd76e266a9cd16f")
	print(DBController.get_passhash_from_login("user111111") == "")

	print(DBController.get_user_data_from_login("user1"))
	print(DBController.get_user_data_from_login("user111111") == None)

	print(DBController.get_user_data_from_login("user1")[4].strftime("%Y-%m-%d %H:%M"))


if __name__ == '__main__':
	test2()

	print(isinstance(DBController.get_last_msg_id(), int))
	print(DBController.get_last_n_msg(1))
	
	#DBController.send_msg(1, "Ogdgfdhfdh")
	#DBController.db_commit()

