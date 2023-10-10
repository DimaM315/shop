from controllers.BaseController import *
from controllers.UserController import UserController
from controllers.ChatController import ChatController



class PageController(BaseController):
    def _call(self, *args, **kwargs):
        page = kwargs.get('page', False)
        
        # Проверяем достаточно ли прав у пользователя для просмотра страницы, которую он запросил.  
        if page not in ["enter", "hello_page"] and not UserController.is_auth():
            # показываем страницу авторизации, если пользователь не авторизован
            # это правило не должно действовать на стр. авторизации и на преветсвенной странице
            return redirect(url_for('enter'))
        if page in ["enter", "hello_page"] and UserController.is_auth():
            return redirect(url_for('home_user_page'))
        if page == 'create_new_user' and not UserController.is_admin():
            abort(404)


        if page == 'hello_page':
            return self.hello_page()
        elif page == 'user':
            return self.user_home_page()
        elif page == 'user_foreign_page' and kwargs.get('user_id', False):
            return self.user_foreign_page(kwargs['user_id'])           
        elif page == 'create_new_user':
            return self.create_new_user_page()
        elif page == 'chat_page':
            return self.chat_page()
        elif page == 'enter':
            return self.enter_page()

        print("Была попытка запросить не существующую страницу")
        abort(404)


    def hello_page(self):
        return render_template('hello_page.html')


    def user_home_page(self):  
        print("\nСессия текущего пользовеля: ", session, '\n')    
        user_data = UserController.get_current_user_data()
        logout_token = models.get_token() 
        session['logout_token'] = logout_token

        return render_template("user_page.html", 
                            is_admin=UserController.is_admin(),
                            yourPage=True,
                            logout_token=logout_token,
                            login=session.get("login", ""), 
                            name=user_data['name'],
                            current_user_name=user_data['name'],
                            created_time=user_data['created_time'])


    def user_foreign_page(self, user_id:int):
        if not isinstance(user_id, int) or not UserController.has_user_with_id(user_id):
            abort(404)
        user_data = UserController.get_user_data(user_id)
        current_user_data = UserController.get_current_user_data()
        logout_token = models.get_token() 
        session['logout_token'] = logout_token

        print("Пользоветль " + current_user_data['name'] + " запросил страницу пользовеля с id:" + str(user_id))
        return render_template("user_page.html", 
                            is_admin=UserController.is_admin(),
                            yourPage=current_user_data['id'] == user_data['id'],
                            logout_token=logout_token,
                            login=user_data['login'], 
                            name=user_data['name'],
                            current_user_name=current_user_data['name'],
                            created_time=user_data['created_time'])


    def create_new_user_page(self):
        has_error = False
        result_msg = ""
        if request.method == 'POST':
            # Была отправка формы.
            # Проверям совпадает ли токен из сессии с токеном который пришёл.
            if session['token_new_user_form'] == int(request.form.get('token')):
                create_result, result_msg = UserController.create_new_user_process(request.form.get('name'), request.form.get('login'), request.form.get('password'))
                has_error = not create_result # Если создание прошло успешно, значит в has_error должен быть False и наоборот.
                print(request.form.get('token') + " токены совпадает.", result_msg)
            else: 
                print("Для текущей сессии не совпали токены авторазации: " + str(session['token_new_user_form']) + " " + request.form.get('token'))
                return redirect('/')
        # Область метода GET
        token_new_user_form = models.get_token() 
        session['token_new_user_form'] = token_new_user_form
        current_user_data = UserController.get_current_user_data()
        return render_template("create_new_user.html", has_error=has_error, token=token_new_user_form, result_msg=result_msg, current_user_name=current_user_data['name'])


    def chat_page(self):
        current_user_data = UserController.get_current_user_data()

        msg_token = models.get_token() 
        session['msg_token'] = msg_token

        logout_token = models.get_token() 
        session['logout_token'] = logout_token

        
        process_responce = make_response(render_template('chat.html', 
                            is_admin=UserController.is_admin(), 
                            messeges=ChatController.get_all_msg(), 
                            msg_token=msg_token, 
                            logout_token=logout_token, 
                            current_user_name=current_user_data['name']))
        
        ChatController.add_msg_cookie(process_responce)
        return process_responce


    def enter_page(self):
        if request.method == 'POST':
            # Была попытка авторизации, проверяем присланные данные.
            # Проверям совпадает ли токен из сессии с токеном который пришёл.
            if session['enter_token'] == int(request.form.get('token')): # приводим к типу число, для возможности сравнения с токеном из сессии
                print(request.form.get('token') + " токены авторазации совпадает")
                if UserController.auth_process(request.form.get('login'), request.form.get('password')): # в объекте request хранятся данные формы
                    print("Авторизация пользователя " + request.form.get('login') + " успешно выполнена")
                    return redirect('user')
                else:
                    print("Пользователь " + request.form.get('login') + " не найден. Проверьте логин и пароль!")
            else: 
                print("Токены авторазации не совпали: " + str(session['enter_token']) + " " + request.form.get('token'))
                return redirect('/')  

        # Эта область для метода GET
        token_for_current_user = models.get_token()
        session['enter_token'] = token_for_current_user
        return render_template("enter.html", has_error=True, token=token_for_current_user)


