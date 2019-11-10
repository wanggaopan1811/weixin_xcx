from app.libs.redprint import RedPrint
from flask import jsonify, request, g, json
from app.models.member import Member
from app.models.cart import MemberCart
from app.service.memberService import memberService
from app.models.food import Food
from app.utils.common import ww
from app.service.cardService import cardService
from app import db

api = RedPrint('card', description='购物车')


@api.route('/add', methods=["GET", 'POST'])
def add():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    try:
        member = g.member
        if not member:
            res['code'] = -1
            res['msg'] = '用户不存在'
            return jsonify(res)

        id = request.form.get('id')  # 食品id
        # print(id,'edddddddddddddddddddddddddd')
        num = int(request.form.get('num'))
        fromtype = int(request.form.get('fromtype'))

        # 参数校验
        food = Food.query.get(id)

        if not food:
            res['code'] = -1
            res['msg'] = '商品不存在'
            return jsonify(res)

        if food.status != 1:
            res['code'] = -1
            res['msg'] = '商品已经下架'
            return jsonify(res)
        if fromtype == 0:
            if num < 1:
                res['code'] = -1
                res['msg'] = '商品数量不对'
                return jsonify(res)

        if num > food.stock:
            res['code'] = -1
            res['msg'] = '库存不足'
            return jsonify(res)
        # 查看自己的购物车是否存在这个商品

        membercart = MemberCart.query.filter_by(member_id=member.id, food_id=id).first()

        if not membercart:
            membercart = MemberCart()
            membercart.food_id = id
            membercart.member_id = member.id
            membercart.quantity = num

            db.session.add(membercart)
            db.session.commit()
        else:
            # 数量加起来
            membercart.quantity = membercart.quantity + num
        db.session.add(membercart)
        db.session.commit()
        # cardService.addCard(member, id, num)
        return jsonify(res)
    except Exception as e:
        res['code'] = -1
        res['msg'] = '参数错误'
        return jsonify(res)


# 展示购物车列表商品
@api.route('/list')
def list():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = '用户不存再在'
        return jsonify(res)
    MemberCarts = MemberCart.query.filter_by(member_id=member.id).all()
    list = []
    totalPrice = 0
    for mc in MemberCarts:
        temp_food = {}
        food = Food.query.get(mc.food_id)
        if not food or food.status != 1:
            continue
        temp_food['id'] = mc.id
        temp_food['food_id'] = mc.food_id
        temp_food['pic_url'] = ww(food.main_image)
        temp_food['name'] = food.name
        temp_food['price'] = str(food.price)
        temp_food['active'] = 'true'
        temp_food['number'] = mc.quantity
        list.append(temp_food)
        totalPrice += mc.quantity * food.price
    # 存入在cardService
    # totalPrice, list = cardService.list(member)

    res['data']['list'] = list
    res['data']['totalPrice'] = str(totalPrice)
    return jsonify(res)

    '''
    1.验证登陆
    2.验证成功后查看购物车
    3.根据购物车查Food表
    4.构建数据(食品数据，总价)
    list: [
            {
            "id": 1080,
            "food_id":"5",
            "pic_url": "/images/food.jpg",
            "name": "小鸡炖蘑菇-1",
            "price": "85.00",
            "active": true,
            "number": 1
        }
    '''


@api.route('/delete', methods=["GET", "POST"])
def delete():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = '用户不存在'
        return jsonify(res)

    ids = request.form.get('ids')
    # print(ids, 'wssssssssssssssssssssssssssssse')
    if not ids:
        res['code'] = -1
        res['msg'] = '参数有误'

        return jsonify(res)
    # 变列表
    ids = json.loads(ids)  # 购物车id

    for id in ids:
        membercart = MemberCart.query.get(id)
        if not membercart:
            continue
        db.session.delete(membercart)
        db.session.commit()
    return jsonify(res)
