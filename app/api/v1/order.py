from app.libs.redprint import RedPrint
from app import db
from app.models.cart import MemberCart
from app.models.address import MemberAddress
from app.models.order import PayOrder, PayOrderItem
from app.models.food import Food
from app.utils.common import ww
import json
from flask import jsonify, request, g, current_app
from app.service.WeChatService import WeChatService
from app.models.member import OauthMemberBind

api = RedPrint('order', description='结算')


# 提交并展示数据
@api.route('/commit', methods=["POST"])
def commit():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    # 接收参数,商品的ids
    ids = request.form.get('ids')
    ids = json.loads(ids)
    type = request.form.get('type')
    num = request.form.get('num')
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = "用户不存在"
        return jsonify(res)
    goods_list = []
    default_address = {}
    total_price = 0
    for id in ids:
        temp_data = {}
        membercart = MemberCart.query.filter_by(food_id=id, member_id=member.id).first()
        food = Food.query.get(id)
        temp_data['id'] = id
        temp_data['name'] = food.name
        temp_data['number'] = membercart.quantity
        temp_data['pic_url'] = ww(food.main_image)
        goods_list.append(temp_data)
        total_price += food.price * membercart.quantity
        # for id in ids:
        #     temp_data = {}
        #     food = Food.query.get(id)
        #     temp_data['id'] = id
        #     temp_data['name'] = food.name
        #     temp_data['number'] = int(num)
        #     temp_data['pic_url'] = ww(food.main_image)
        #     goods_list.append(temp_data)
        #     total_price += food.price * int(num)

        memberaddress = MemberAddress.query.filter_by(is_default=1).first()
        # 地址
        default_address['id'] = memberaddress.id
        default_address["name"] = memberaddress.nickname
        default_address["mobile"] = memberaddress.mobile
        default_address["detail"] = memberaddress.address

        # total_price = yun_orice + pay_price
    res['data']['goods_list'] = goods_list
    res['data']['total_price'] = str(total_price)
    res['data']['default_address'] = default_address
    return jsonify(res)


@api.route('/create', methods=["POST"])
def create():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    # try:
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = "用户不存在"
        return jsonify(res)
    ids = request.form.get('ids')  # 商品的ids
    address_id = request.form.get('address_id')
    print(address_id,'iddddddddddddddddddddddddddddddddddddddd')
    note = request.form.get('note')
    ids = json.loads(ids)
    # 0根据ids查看购物车
    yun_price = 0
    pay_price = 0
    for id in ids:
        membercart = MemberCart.query.filter_by(member_id=member.id, food_id=id).first()
        if not membercart:
            continue

        food = Food.query.get(id)  # 差食品表
        if not food or food.status != 1:
            continue
        pay_price += food.price * membercart.quantity
    memberaddress = MemberAddress.query.get(address_id)
    if not memberaddress:
        res['code'] = -1
        res['msg'] = '地址不存在'
        return jsonify(res)

    # 1生成订单
    payorder = PayOrder()

    payorder.order_sn = geneOrderSn()
    payorder.total_price = pay_price + yun_price
    payorder.yun_price = yun_price
    payorder.pay_price = pay_price
    payorder.note = note
    payorder.status = -8  # 待支付
    payorder.express_status = -1  # 代发货
    payorder.express_info = memberaddress.showAddress()
    payorder.comment_status = -1  # 带评论
    payorder.member_id = member.id  # 带评论

    db.session.add(payorder)

    # 2扣库存--悲、乐 锁
    foods = db.session.query(Food).filter(Food.id.in_(ids)).with_for_update().all()
    temp_stock = {}  # 临时库存
    for food in foods:
        temp_stock[food.id] = food.stock

    for id in ids:
        membercart = MemberCart.query.filter_by(member_id=member.id, food_id=id).first()

        # if not membercart:
        #     res['code'] = -1
        #     res['msg'] = '购物车不存在'
        #     return jsonify(res)
        aa = int(membercart.quantity)
        if aa > int(temp_stock[id]):
            res['code'] = -1
            res['msg'] = '库存不足'
            return jsonify(res)

        food = db.session.query(Food).filter(Food.id == id).update({
            'stock': temp_stock[id] - membercart.quantity
        })
        if not food:
            raise Exception('更新失败')
        food = Food.query.get(id)
        # 3生成订单的商品从表
        payorderitem = PayOrderItem()
        payorderitem.quantity = membercart.quantity
        payorderitem.price = food.price
        payorderitem.note = note
        payorderitem.status = 1
        payorderitem.pay_order_id = payorder.id
        payorderitem.member_id = member.id
        payorderitem.food_id = id

        db.session.add(payorderitem)

        # 4清空下单的购物车商品
        db.session.delete(membercart)
    # 提交
    db.session.commit()
    # except Exception as e:
    #     print(e, 'wwwwwwwwwwwwwwwwwyichagn   wwwwwwwwwwwwwwwwwwwwwww')
    #     db.session.rollback()
    #     res['code'] = -1
    #     res['msg'] = '出现异常'
    #     return jsonify(res)

    return jsonify(res)


# 加密
import hashlib, time, random


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


##从购物车将物品拿出来，生成订单展示出来
@api.route('/list', methods=["GET"])
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
    print(status, '-------------------===========')
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = '用户不存在'
        return jsonify(res)
    print(member, '------------------------------')
    order_list = []
    # 根据id获取购物车的数据
    print()
    PayOrders = PayOrder.query.filter_by(member_id=member.id, status=status).all()
    for payorder in PayOrders:
        temp_data = {}
        temp_data['status'] = payorder.status
        temp_data['status_desc'] = payorder.status_desc
        temp_data['date'] = payorder.create_time.strftime('%Y-%m-%d %H-%M-%S')
        temp_data['order_number'] = payorder.create_time.strftime('%Y%m%d%H%M%S') + str(payorder.id).zfill(5)
        temp_data['order_sn'] = payorder.order_sn
        temp_data['note'] = payorder.note
        temp_data['total_price'] = str(payorder.total_price)
        # print(temp_data['order_sn'],'snsnsnnnnsnnsnsnsnsnsnnssnnsnsn')

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


# 支付
@api.route('/pay')
def pay():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member
    req = request.values
    # 接受参数
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    print(order_sn,'======================================')
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
        'appid': current_app.config['APP_ID'],  # 小程序id
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


# @api.route("/callback", methods=["POST"])
# def orderCallback():
#     result_data = {
#         'return_code': 'SUCCESS',
#         'return_msg': 'OK'
#     }
#     header = {'Content-Type': 'application/xml'}
#     target_wechat = WeChatService(merchant_key=current_app.config['PAYKEY'])
#     # 解析微信推送过来的xml 支付结果  改成字典
#     callback_data = target_wechat.xml_to_dict(request.data)
#
#     # 取出这里面sign
#     sign = callback_data['sign']
#
#     # 在pop掉sign
#     callback_data.pop('sign')
#
#     # 在把这个字典进行签名 返回一个sign
#     gene_sign = target_wechat.create_sign(callback_data)  # 在加密
#     # 如果取出的sign和加密后的sign不一样
#     if sign != gene_sign:
#         result_data['return_code'] = result_data['return_msg'] = 'FAIL'
#         return target_wechat.dict_to_xml(result_data), header
#     # 如果返回的不等于成功
#     if callback_data['result_code'] != 'SUCCESS':
#         result_data['return_code'] = result_data['return_msg'] = 'FAIL'
#         return target_wechat.dict_to_xml(result_data), header
#     # 订单号取出来
#     order_sn = callback_data['out_trade_no']
#
#     # 根据订单查这个订单的信息
#     pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
#     if not pay_order_info:
#         result_data['return_code'] = result_data['return_msg'] = 'FAIL'
#         return target_wechat.dict_to_xml(result_data), header
#
#     # 如果付款的金额和推送过来的支付金额不一样
#     if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
#         result_data['return_code'] = result_data['return_msg'] = 'FAIL'
#         return target_wechat.dict_to_xml(result_data), header
#
#     if pay_order_info.status == -8:
#         return target_wechat.dict_to_xml(result_data), header
#
#     # 把订单更新待发货
#     OrderService.orderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id']})
#     return target_wechat.dict_to_xml(result_data), header
