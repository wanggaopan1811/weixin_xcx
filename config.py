class Config():
    SECRET_KEY = 'rgrehbiuwegrieg'
    # 设置连接数据库的URL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/weixin_xcx'

    # 数据库和模型类同步修改
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    SQLALCHEMY_ECHO = True
    # 密钥
    APP_SECRET = 'df14d0d237500cdff5bcc0cea6d2a366'
    APP_ID = 'wxd9b0e91350040fff'
    # APP_ID = 'HG1Abtg20dWEGG1pfSHG1UVWHb'
    MCH_ID = '532156521325'#商户号id
    PAYKEY = 'www254263#$%EW' #商户密钥
    CALLBACK_URL = '/api/vi/order/callback'

    DOMAIN = 'aasddrrtty'
    NEXT_URL = 'http://127.0.0.1:5000/static/'
    IGNORE_URLS = ['/api/v1/member/login',
                   '/api/v1/member/cklogin',
                   '/api/v1/food/foods',
                   '/api/v1/food/zhanshi',
                   '/api/v1/food/info']


# 线上环境-
class ProductingConfig(Config):
    DEBUG = False


# 生产环境
class DevelopmentConfig(Config):
    DEBUG = True


mapping_config = {
    'pro': ProductingConfig,
    'dev': DevelopmentConfig,
}
