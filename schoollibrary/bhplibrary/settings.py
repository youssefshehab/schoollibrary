class Config(onject):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    DATABASE_URI = 'sqlite:////tmp/test.db'
    DEBUG = False
    TEST = False

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    DATABASE_URI = 'sqlite:////tmp/test.db'
    DEBUG = TRUE
    TEST = False
