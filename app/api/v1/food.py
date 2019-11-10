from app.libs.redprint import RedPrint
from flask import request, jsonify, current_app
import requests
from app.utils.common import ww
from app import db
from app.models.food import Food, Category
from app.models.address import MemberAddress
from app.models.cart import MemberCart
from app.models.member import Member, OauthMemberBind

api = RedPrint('food', description='会员模块')


@api.route('/foods')
def foods():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    categories = []
    categories.append(
        {
            'id': 0,
            'name': "all"
        }
    )
    all_category = Category.query.filter_by(status=1).order_by(Category.weight.desc()).all()
    for category in all_category:
        item_data = {}
        item_data['id'] = category.id
        item_data['name'] = category.name
        categories.append(item_data)

    banners = []
    foods = Food.query.filter_by(status=1).order_by(Food.month_count.desc()).limit(3).all()
    for food in foods:
        temp_data = {}
        temp_data['id'] = food.id
        temp_data['pic_url'] = ww(food.main_image)
        banners.append(temp_data)
    res['data']['categories'] = categories
    res['data']['banners'] = banners
    return jsonify(res)


# 展示
@api.route('/zhanshi', methods=["GET"])
def zhanshi():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    try:
        cid = request.args.get('cid')
        page = request.args.get('page')
        print(cid)
        if not cid:
            cid = '0'

        if not page:
            page = '1'
        cid = int(cid)
        page = int(page)

        '''
        每页一个数据
        '''
        pagesize = 1
        # 分页公式
        offset = (page - 1) * pagesize

        goods = []
        query = Food.query.filter_by(status=1)
        print('经过')
        if cid == 0:
            foods = query.offset(offset).limit(pagesize).all()
            print(len(foods))
        else:
            foods = query.filter_by(cat_id=cid).offset(offset).limit(pagesize).all()
            print(len(foods), '22222')
            # print('我也来过')

        for food in foods:
            zs = {}
            zs['id'] = food.id
            zs["name"] = food.name
            zs["min_price"] = str(food.price)
            zs["price"] = str(food.price)
            zs['pic_url'] = ww(food.main_image)
            goods.append(zs)
        res['data']['goods'] = goods
        # 判断有没有数据，有数据返回1 没数据返回0
        if len(foods) < pagesize:
            res['data']['ismore'] = 0
        else:
            res['data']['ismore'] = 1
        return jsonify(res)
    except Exception as e:
        res['code'] = -1
        res['msg'] = "参数有误"
        return jsonify(res)


# 详情
@api.route('/info')
def info():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    try:
        id = request.args.get('id')
        print(id, 'idiiididdididiididididiid')
        if not id:
            res['code'] = -1
            res['msg'] = '参数不可为空'
            return jsonify(res)

        id = int(id)
        if id <= 0:
            res['code'] = -1
            res['msg'] = '参数有误a '
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
        food = Food.query.get(id)
        info = {}
        info['id'] = food.id
        info['name'] = food.name
        info['summary'] = food.summary
        info['total_count'] = food.total_count
        info['comment_count'] = food.comment_count
        info['stock'] = food.stock
        info['price'] = str(food.price)
        info['main_image'] = ww(food.main_image)
        info['pics'] = ww(food.main_image), ww(food.main_image), ww(food.main_image)
        res['data']['info'] = info
        return jsonify(res)
    except Exception  as e:
            res['code'] = -1
            res['msg'] = "参数有误"
            return jsonify(res)

