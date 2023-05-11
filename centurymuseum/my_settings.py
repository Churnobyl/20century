DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_museum', # 연동할 mysql db 이름
        'USER': 'root', # db 접속 계정명
        'PASSWORD': 'louisn123123', # 해당 계정 비밀번호
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}