from app.libs.redprint import RedPrint
from app import db
from app.models.cart import MemberCart
from app.models.address import MemberAddress
from app.models.order import PayOrder, PayOrderItem
from app.models.food import Food
from app.utils.common import ww
from app.models.member import OauthMemberBind
from app.service.WeChatService import WeChatService
from app.service.order_servcie import OrderService
import json

import hashlib
import time
import random

from flask import jsonify, request, g,current_app

api = RedPrint('order', description='订单模块')


@api.route('/index', methods=['POST'])
def center():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    ids = request.form.get('ids')  # 商品的ids

    ids = json.loads(ids)  # 转成列表

    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = '用户不存'
        return jsonify(res)
    '''
     goods_list: [
            {
                id: 22,
                name: "小鸡炖蘑菇",
                price: "85.00",
                pic_url: "/images/food.jpg",
                number: 1,
            },
            {
                id: 22,
                name: "小鸡炖蘑菇",
                price: "85.00",
                pic_url: "/images/food.jpg",
                number: 1,
            }
        ],
    
         default_address: {
            name: "编程浪子",
            mobile: "12345678901",
            detail: "上海市浦东新区XX",
        },
        yun_price: "1.00",
        pay_price: "85.00",
        total_price: "86.00",
        params: null
    '''

    yun_price = 0
    pay_price = 0
    goods_list = []
    for id in ids:
        temp_data = {}
        membercart = MemberCart.query.filter_by(food_id=id, member_id=member.id).first()
        food = Food.query.get(id)

        # 可能需要判断商品是否存在 和状态
        temp_data['id'] = id
        temp_data['name'] = food.name
        temp_data['price'] = str(food.price)
        temp_data['pic_url'] = ww(food.main_image)
        temp_data['number'] = membercart.quantity
        goods_list.append(temp_data)

        pay_price += food.price * membercart.quantity

    memberaddress = MemberAddress.query.filter_by(member_id=member.id, is_default=1).first()

    # 地址
    default_address = {}
    default_address['id'] = memberaddress.id
    default_address['name'] = memberaddress.nickname
    default_address['mobile'] = memberaddress.mobile
    default_address['address'] = memberaddress.showAddress()

    total_price = yun_price + pay_price
    # 查询此会员的默认地址
    # 计算总价

    res['data']['goods_list'] = goods_list
    res['data']['default_address'] = default_address
    res['data']['total_price'] = str(total_price)
    res['data']['yun_price'] = str(yun_price)
    res['data']['pay_price'] = str(pay_price)
    # 返回

    return jsonify(res)


@api.route('/create', methods=['POST'])
def create():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    # try:
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = '用户不存'
        return jsonify(res)
    ids = request.form.get('ids')  # 商品的ids
    address_id = request.form.get('address_id')
    note = request.form.get('note')

    ids = json.loads(ids)
    pay_price = 0
    yun_price = 0
    # 0、根据ids去购物车
    for id in ids:
        membercart = MemberCart.query.filter_by(member_id=member.id, food_id=id).first()

        if not membercart:  # 是否合适
            continue

        food = Food.query.get(id)  # 查食品表

        if not food or food.status != 1:
            continue

        pay_price += food.price * membercart.quantity

    memberaddress = MemberAddress.query.get(address_id)  # 查地址

    if not memberaddress:
        res['code'] = -1
        res['msg'] = '地址不存在'
        return jsonify(res)

        # 1、生成订单
    payorder = PayOrder()
    payorder.order_sn = geneOrderSn()  # 唯一
    payorder.total_price = yun_price + pay_price
    payorder.yun_price = yun_price
    payorder.pay_price = pay_price
    payorder.note = note
    payorder.status = -8  # 待付款
    payorder.express_status = -1  # 待发货
    payorder.express_address_id = address_id
    payorder.express_info = memberaddress.showAddress()
    payorder.comment_status = -1  # 待评论
    payorder.member_id = member.id  # 待评论

    db.session.add(payorder)

    # 2、扣库存--并发问题 Food  悲观锁----乐观锁
    foods = db.session.query(Food).filter(Food.id.in_(ids)).with_for_update().all()
    temp_stock = {}  # 临时的库存

    # {1:99,2:100}
    for food in foods:
        temp_stock[food.id] = food.stock
    for id in ids:
        membercart = MemberCart.query.filter_by(member_id=member.id, food_id=id).first()

        if not membercart:
            res['code'] = -1
            res['msg'] = '购物车不存在'
            return jsonify(res)

        if membercart.quantity > temp_stock[id]:
            res['code'] = -1
            res['msg'] = '库存不足'
            return jsonify(res)

        food = db.session.query(Food).filter(Food.id == id).update({
            'stock': temp_stock[id] - membercart.quantity
        })

        if not food:
            raise Exception('更新失败')

        food = Food.query.get(id)  # 查

        # 3、生成订单的商品从表
        payorderitem = PayOrderItem()
        payorderitem.quantity = membercart.quantity
        payorderitem.price = food.price
        payorderitem.note = note
        payorderitem.status = 1
        payorderitem.pay_order_id = payorder.id
        payorderitem.member_id = member.id
        payorderitem.food_id = id

        db.session.add(payorderitem)

        db.session.delete(membercart)  # 删除已经下单的购物车

    db.session.commit()
    # except Exception as e:
    #     print(e,1111111111111111111)
    #     db.session.rollback()
    #     res['code'] = -1
    #     res['msg'] = '出现异常'
    #     return jsonify(res)

    return jsonify(res)


def geneOrderSn():
    m = hashlib.md5()
    sn = None
    while True:
        str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 9999999))
        m.update(str.encode("utf-8"))
        sn = m.hexdigest()
        if not PayOrder.query.filter_by(order_sn=sn).first():
            break
    return sn


@api.route('/list')
def list():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    '''
    order_list: [
                {
					status: -8,
                    status_desc: "待支付",
                    date: "2018-07-01 22:30:23",
                    order_number: "20180701223023001",
                    note: "记得周六发货",
                    total_price: "85.00",
                    goods_list: [
                        {
                            pic_url: "/images/food.jpg"
                        },
                        {
                            pic_url: "/images/food.jpg"
                        }
                    ]
                }
            ]
    
    '''
    status = request.args.get('status')
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = '用户不存'
        return jsonify(res)
    # 1  ---> 00001
    order_list = []
    payorders = PayOrder.query.filter_by(member_id=member.id, status=status).all()
    for payorder in payorders:
        temp_data = {}
        temp_data['status'] = payorder.status
        temp_data['status_desc'] = payorder.status_desc
        temp_data['date'] = payorder.create_time.strftime('%Y-%m-%d %H:%M:%S')
        temp_data['note'] = payorder.note
        temp_data['total_price'] = str(payorder.total_price)
        temp_data['oder_sn'] = payorder.oder_sn
        temp_data['order_number'] = payorder.create_time.strftime('%Y%m%d%H%M%S') + str(payorder.id).zfill(5)
        goods_list = []
        # 查订单商品
        payorderitems = PayOrderItem.query.filter_by(pay_order_id=payorder.id).all()
        for payorderitem in payorderitems:
            food = Food.query.get(payorderitem.food_id)
            temp_food = {}
            temp_food['pic_url'] = ww(food.main_image)

            goods_list.append(temp_food)

        temp_data['goods_list'] = goods_list

        order_list.append(temp_data)
    res['data']['order_list'] = order_list
    return jsonify(res)


@api.route('/pay')
def pay():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    # 接受参数
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    # 去库找到该订单
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~"
        return jsonify(resp)
    # 找到该会员的信息
    oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
    if not oauth_bind_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙。请稍后再试~~2"
        return jsonify(resp)
    #http://127.0.0.1:5000/api/v1/order/callback
    notify_url = current_app.config['DOMAIN'] + current_app.config['CALLBACK_URL']
    # 为了将来推送支付结果

    target_wechat = WeChatService(merchant_key=current_app.config['PAYKEY'])  # 商户密钥 目前没有

    data = {
        'appid': current_app.config['APPID'],  # 小程序id
        'mch_id': current_app.config['MCH_ID'],  # 商户号没有
        'nonce_str': target_wechat.get_nonce_str(),  # 随机字符串
        'body': '订餐',  # 商品描述
        'out_trade_no': pay_order_info.order_sn,  # order_sn
        'total_fee': int(pay_order_info.total_price * 100),  # 钱  单位是分
        'notify_url': notify_url,  # 回调地址
        'trade_type': "JSAPI",  # jsai
        'openid': oauth_bind_info.openid,  # 开发平台的id
        'spbill_create_ip': '127.0.0.1'  # ip地址
    }

    #
    pay_info = target_wechat.get_pay_info(pay_data=data)

    # # 保存prepay_id为了后面发模板消息
    pay_order_info.prepay_id = pay_info['prepay_id']
    db.session.add(pay_order_info)
    db.session.commit()

    resp['data']['pay_info'] = pay_info
    return jsonify(resp)

@api.route("/callback", methods=["POST"])
def orderCallback():
    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK'
    }
    header = {'Content-Type': 'application/xml'}
    target_wechat = WeChatService(merchant_key=current_app.config['PAYKEY'])
    # 解析微信推送过来的xml 支付结果  改成字典
    callback_data = target_wechat.xml_to_dict(request.data)

    # 取出这里面sign
    sign = callback_data['sign']

    # 在pop掉sign
    callback_data.pop('sign')

    # 在把这个字典进行签名 返回一个sign
    gene_sign = target_wechat.create_sign(callback_data)  # 在加密
    # 如果取出的sign和加密后的sign不一样
    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    # 如果返回的不等于成功
    if callback_data['result_code'] != 'SUCCESS':
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    # 订单号取出来
    order_sn = callback_data['out_trade_no']

    # 根据订单查这个订单的信息
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 如果付款的金额和推送过来的支付金额不一样
    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if pay_order_info.status == -8:
        return target_wechat.dict_to_xml(result_data), header

    # 把订单更新待发货
    OrderService.orderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id']})
    return target_wechat.dict_to_xml(result_data), header
