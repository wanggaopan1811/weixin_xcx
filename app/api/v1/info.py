from app.libs.redprint import RedPrint
from flask import request, jsonify,current_app
import requests
from app.utils.common import ww
from app import db
from app.models.food import Food,Category
from app.models.member import Member,OauthMemberBind


api = RedPrint('info', description='会员模块')
@api.route('info')
def info():
    res = {'code': 1, 'msg': '成功', 'data': {}}

    id = request.args.get('id')

    if not id :
        res['code'] = -1
        res['msg'] = '参数不可为空'
        return jsonify(res)
    id = int(id)

    if id <= 0:
        res['code'] = -1
        res['msg'] = '参数有误'
        return jsonify(res)
    '''
    //"id": e.id,
    // "name": "小鸡炖蘑菇",
    // "summary": '<p>多色可选的马甲</p><p><img src="http://www.timeface.cn/uploads/times/2015/07/071031_f5Viwp.jpg"/></p><p><br/>相当好吃了</p>',
    // "total_count": 2,
    // "comment_count": 2,
    // "stock": 2,
    // "price": "80.00",
    // "main_image": "/images/food.jpg",
    // "pics": [ '/images/food.jpg','/images/food.jpg' ]
    '''
    food  =Food.query.get(id)
    info = {}
    info['id'] = food.id
    info['name'] = food.name
    info['summary'] = food.summary
    info['total_count'] = food.total_count
    info['comment_count'] = food.comment_count
    info['stock'] = food.stock
    info['price'] = str(food.price)
    info['main_image'] = ww(food.main_image)
    info['pics'] = ww(food.main_image),ww(food.main_image),ww(food.main_image)
    info['data']['info'] = info

    '''
    一个商品对应多个图片 图片表
    以空间换时间
    
    食品表  图片表
    '''
    return jsonify(res)
