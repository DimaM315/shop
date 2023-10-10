from controllers.BaseController import *
from controllers.DBController import DBController
from controllers.UserController import UserController


class ChatController:

	@staticmethod
	def chat_proccess():
		is_auto = True
		if not is_auto:
			# показываем страницу авторизации
			return redirect('enter')

		if request.method == 'POST':
			# пользователь отправил сообщение
			if session['msg_token'] == int(request.form.get('token')): 
				# сравниваем токены, нужно чтобы ни кто не мог с другого сайта отправлять от имени 
				# пользователя с активной сессией отправлять сообщения
				return ChatController.save_message(request.form.get('msg'))
		elif request.method == 'GET':
			# запрос на получение сообщений
			# пока что отправляем сразу все сообщения в чате. Далее добавим фильт чтобы получать порциями
			if session['msg_token'] == int(request.args.get('token')) and UserController.is_auth():
				return ChatController.get_avialable_messages()

		return "request was not proccessed"


	@staticmethod
	def get_all_msg():
		# Получаем все сообщения из базы данных. Получение больших обьёмов сообщений, может сказаться на производительности.
		return DBController.get_all_messeges()


	@staticmethod
	def add_msg_cookie(resp):
		# Добавляем в куки id последнего сообщения, чтобы фронтенд от его значения запрашивал сообщения.
		last_msg_id = DBController.get_last_msg_id()
		resp.set_cookie("last_msg_id", value=str(last_msg_id), max_age=None)


	@staticmethod
	def save_message(msg_text:str):
		# Сохраняем сообщение в бд.
		if models.check_valid_msg(msg_text) == False:
			return "Сообщение содержет недопустимые символы!"


		current_user_data = UserController.get_current_user_data()
		DBController.send_msg(user_id=current_user_data['id'], msg_text=msg_text)
		DBController.db_commit()
		return "Сообщение обработано"


	@staticmethod
	def get_avialable_messages():
		# Сколько сообщений доступно, из последнего id из бд вычитаем id который пришёл от пользователя.
		how_mush_available = DBController.get_last_msg_id() - int(request.args.get('user_current_last_msg_id'))
		if how_mush_available > 0:
			# Если больше 0, значит в бд есть актуальные сообщения для пользователя. Так же обновляем куки.
			process_responce = make_response(DBController.get_last_n_msg(how_mush_available), 200)# получаем эти сообщения.
			ChatController.add_msg_cookie(process_responce) # обновляем last_msg_id
			return process_responce
		return []