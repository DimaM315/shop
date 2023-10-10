class  Configuration(object):
	DEBUG = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/BS_flask'
	SECRET_KEY = 'secret'
	
	#flack sequrity
	SECURITY_PASSWORD_SALT = 'sault'
	SECURITY_PASSWORD_HASH = 'sha512_crypt'
