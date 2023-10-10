from controllers.BaseController import *
from controllers.DBController import DBController


class UserController:
    
    @staticmethod
    def auth_process(login:str, password:str)->bool:
        # Функция отвечает за логику авторизации пользователя. 
        # Если пользователь успешно прошёл авторизаци, возвращаем True. Иначе False

        # Проверям существуют ли набор login и хэш от password, если да, то добавляем их в сессию.
        password_hash = models.get_hash(password)
        if DBController.get_passhash_from_login(login) == password_hash: 
            session['login'] = login
            session['password_hash'] = password_hash
            return True
        return False


    @staticmethod
    def create_new_user_process(name:str, login:str, password:str)->(bool, str):
        # Функция отвечает за добавление нового пользователя в базу данных.
        # Валидируем данные. Создаём пользователя с ролью user. 
        login = login.strip()
        name = name.strip()
        
        check_results, result_msg = models.check_valid_login(login)
        if check_results == False:
            return False, result_msg

        check_results, result_msg = models.check_valid_password(password)
        if check_results == False:
            return False, result_msg

        check_results, result_msg = models.check_valid_username(name)
        if check_results == False:
            return False, result_msg        
        
        color_in_chat = UserController.generate_color_from_chat()
        DBController.create_new_user(name, login, models.get_hash(password), color_in_chat)
        DBController.db_commit()
        return True, "Создаём нового пользователя: {"+login+";"+password+";"+name+"}"

        

    @staticmethod
    def is_auth()->bool:
        # Проверям по данным из сессии авторизован ли пользователь.
        return session.get('password_hash', '') == DBController.get_passhash_from_login(session.get('login', ''))


    @staticmethod
    def is_admin()->str:
        # проверям роль админ у данного пользователя или нет
        return "admin" == DBController.get_role_from_login(session.get('login', ''))


    @staticmethod
    def logout():
        # Удаляем данные сессии. Так же проверяем токен логаута.
        if UserController.is_auth() and session['logout_token'] == int(request.form.get('logout_token')):
            print("Пользователь " + session['login'] + " вышел из аккаунта")
            session.pop('login', None)
            session.pop('password', None)
        return redirect('/')


    @staticmethod
    def get_current_user_data()->dict:
        # Пока что, каждый раз при запросе данных авторизованного пользователя, каждый раз делаем запрос к бд.
        data = DBController.get_user_data_from_login(session['login'])
        return [] if data is None else {'name':data[1], 'id':data[0], 'created_time':data[4].strftime("%Y-%m-%d %H:%M"), 'login':session['login']}


    @staticmethod
    def get_user_data(user_id:int)->dict:
        data = DBController.get_user_data_from_id(user_id)
        return [] if data is None else {'name':data[1], 'id':data[0], 'created_time':data[4].strftime("%Y-%m-%d %H:%M"), 'login':data[2]}


    @staticmethod
    def has_user_with_id(user_id:int)->bool:
        return DBController.get_user_data_from_id(user_id) != None

    @staticmethod
    def generate_color_from_chat()->str:
        # Выбираем цвет для ника в чате. Выбор из тех цветов, которые подходят под бекграунд чата.
        color_avialable = ['red', 'green', 'blue', 'violet', 'teal', 'darkgoldenrod', 'darkmagenta', 'maroon', 'orange', 'navy']
        return random.choice(color_avialable)