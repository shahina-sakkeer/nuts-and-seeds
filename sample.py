from decouple import config, Csv

SECRET_KEY = config('SECRET_KEY')
print(SECRET_KEY)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('postgres'),
        'USER':'admin',
        'PASSWORD':'admin',
        'HOST':'localhost'
    }
}

print()