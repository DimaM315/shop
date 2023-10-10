# Здесь будут храниться вспомогательные функции

import random
import hashlib
import re


def get_token()->int:
	# возвращает случайное число от 0 до 10^20 - такое число будет токеном
	return int(random.random() * 10**20)


def get_hash(text:str)->str:
	"""
	Используется статическая соль. Имеет смысл применить метод динамечской соли
	для увеличения времени подбора паролей в случае слива базы данных. Но т.к данные не критичны
	и пароли за
	"""
	SOUL = "secret_word" # соль не должна храниться в открытом виде
	m = hashlib.sha256() # Задаём хэш функцию sha256
	m.update((text + SOUL).encode()) # Применяем её к нашему тексту + соли
	return m.hexdigest() # возвращаем хэш в 16ти ричной форме



### Функции валидации ###

# Здесь задаются правила валидации. Пользователь может отправлять строки на сервер в формах: enter, create_new_user, chat
# Базе данных параметры полей:
# name varchar(20) NOT NULL, Допустимые символы: а-Я+" "+a-Я
# login varchar(50) NOT NULL UNIQUE, Допустимые символы: a-Z0-9
# password varchar(64) NOT NULL, Допустимые символы: a-Z0-9
# message text NOT NULL, Допустимые символы: a-Za-Z0-9!.,?"'()+-=:%
#
# Длинна: login 4-20; password 6-20; name 5-30; msg 1-200;


def check_valid_msg(msg:str)->bool:
	err_msg = ""
	if 0 == len(msg) or len(msg) > 200:
		err_msg = "Длинна сообщения должна быть от 4 до 20 символов!"
		return False, err_msg
	if re.search(re.compile("[^=a-zA-Zа-яА-Я0-9!,.?\"\'()+-:%]"), msg.replace(" ", "")) is not None:
		err_msg = "Запрещённый спец символ в сообщении(будет удалён)."
		return False, err_msg
	return True, err_msg


def check_valid_login(login:str)->bool:
	err_msg = ""
	if 4 > len(login) or len(login) > 20:
		err_msg = "Длинна логина должна быть от 4 до 20 символов!"
		return False, err_msg
	if re.search(re.compile("[^a-zA-Z0-9]"), login) is not None:
		err_msg = "Логин долджен содержать только буквы латинского алфавита или цифры."
		return False, err_msg
	return True, err_msg


def check_valid_password(password:str)->bool:
	err_msg = ""
	if 6 > len(password) or len(password) > 20:
		err_msg = "Длинна пароля должна быть от 6 до 20 символов!"
		return False, err_msg
	if re.search(re.compile("[^a-zA-Z0-9]"), password) is not None:
		err_msg = "Пароль долджен содержать только буквы латинского алфавита или цифры."
		return False, err_msg
	return True, err_msg


def check_valid_username(username:str)->bool:
	err_msg = ""
	if 5 > len(username) or len(username) > 30:
		err_msg = "Длинна имени должна быть от 5 до 30 символов!"
		return False, err_msg
	if " " not in username:
		err_msg = "Напишите имя и фамилию сотрудника через пробел!"
		return False, err_msg
	if re.search(re.compile("[^а-яА-Я]"), username.replace(" ", "")) is not None:
		err_msg = "Имя и фамилия должны содержать только буквы русского алфавита."
		return False, err_msg
	return True, err_msg



# Тесты:
def test_check_username():
	wrong_usernames = ["", "ase", ":54", "'ppppp", "Gf ; select", "54yyrt54645jjjjjjjjjjjgf43fffff", "Имя Фамилия1", "Ivan Ivanov"]
	for item in wrong_usernames:
		if check_valid_username(item)[0]:
			print("Test: test_check_username was falied! by item: " + item)
			return False

	right_usernames = ["Ян Ко", "Имя Фамилия", "Навпавр Исчцукунукыйцййкееииа"]
	for item in right_usernames:
		if not check_valid_username(item)[0]:
			print("Test: test_check_username was falied! by item: " + item)
			return False

	print("Test: test_check_username was succesful complited!")
	return True


def test_check_password():
	wrong_passwords = ["", "5smbl", ":54", "'ppppp", "Gf ; select", "54yyrt54645jjjjjjjjjjjmore20", "Имя Фамилия1", "Ivan Ivanov"]
	for item in wrong_passwords:
		if check_valid_password(item)[0]:
			print("Test: test_check_password was falied! by item: " + item)
			return False

	right_passwords = ["only9smbl", "pass123", "rightPASS"]
	for item in right_passwords:
		if not check_valid_password(item)[0]:
			print("Test: test_check_password was falied! by item: " + item)
			return False

	print("Test: test_check_password was succesful complited!")
	return True


def test_check_login():
	wrong_login = ["", "3sm", ":54", "'ppppp", "Gf ; select", "54yyrt54645jjjjjjjjjjjmore20", "Имя Фамилия1", "Ivan Ivanov"]
	for item in wrong_login:
		if check_valid_login(item)[0]:
			print("Test: test_check_login was falied! by item: " + item)
			return False

	right_login = ["only9smbl", "pass123", "rightLOGIN"]
	for item in right_login:
		if not check_valid_login(item)[0]:
			print("Test: test_check_login was falied! by item: " + item)
			return False

	print("Test: test_check_login was succesful complited!")
	return True


def test_check_msg():
	wrong_msg = ["", "3sm;", "@$", "'ppppp*", "Gf ; select", "&msg", "Имя Фамилия1$", "Ivan Ivanov\\", "msg\\"]
	for item in wrong_msg:
		if check_valid_msg(item)[0]:
			print("Test: test_check_msg was falied! by item: " + item)
			return False

	right_login = ["only9smbl", "pass123", "rightLOGIN", "Сообщение Hello !!!"]
	for item in right_login:
		if not check_valid_msg(item)[0]:
			print("Test: test_check_msg was falied! by item: " + item)
			return False

	print("Test: test_check_msg was succesful complited!")
	return True


if __name__ == '__main__':
	test_check_username()
	test_check_password()
	test_check_login()
	test_check_msg()

	"""
	print(check_valid_username("ase"))
	print(check_valid_username(":54"))
	print(check_valid_username("Имя Фамилия1"))
	print(check_valid_username("Ivan Ivanov"))
	

	print(check_valid_password("'ppppp"))
	
	print(check_valid_login("3sm"))
	print(check_valid_login("Gf ; select"))
	print(check_valid_login("54yyrt54645jjjjjjjjjjjmore20"))
	print(check_valid_login("only9smbl"))

	

	print(check_valid_msg(""))
	print(check_valid_msg("@$"))
	print(check_valid_msg("Имя Фамилия1$"))""" 

	print(check_valid_login("user2"))
	print(check_valid_password("user22"))