from app.libs.redprint import RedPrint
from flask import request, jsonify, g
from app.models.address import MemberAddress
from app.models.order import PayOrder,PayOrderItem
from app.models.member import Member
from app.models.comment import MemberComments
from app.models.address import MemberAddress
from app import db
import json

api = RedPrint(name='comment', description='评价视图')


@api.route('/add', methods=['POST'])
def add():
    resp = {'code': 1, 'msg': '成功', 'data': {}}

    member = g.member

    if not member:
        resp['code'] = -1
        resp['msg'] = '验证失败'
        return jsonify(resp)

    order_sn = request.form.get('order_sn')
    content = request.form.get('content')
    score = request.form.get('score')

    if not all([order_sn, content, score]):
        resp['code'] = -1
        resp['msg'] = '参数不全'
        return jsonify(resp)

    if score not in ['10', '6', '0']:
        resp['code'] = -1
        resp['msg'] = '分数不对'
        return jsonify(resp)

    payorder = PayOrder.query.filter_by(order_sn=order_sn).first()

    if not payorder:
        resp['code'] = -1
        resp['msg'] = '订单不存在'
        return jsonify(resp)

    membercomments = MemberComments()
    membercomments.pay_order_id = payorder.id
    membercomments.member_id = member.id
    membercomments.score = score
    membercomments.content = content

    db.session.add(membercomments)

    payorder.status = 1
    db.session.add(payorder)
    db.session.commit()

    return jsonify(resp)


@api.route('/list1')
def list1():
    resp = {'code': 1, 'msg': '成功', 'data': {}}

    member = g.member

    if not member:
        resp['code'] = -1
        resp['msg'] = '验证失败'
        return jsonify(resp)

    membercomments = MemberComments.query.filter_by(member_id=member.id).all()
    '''
     list: [
             {
                 date: "2018-07-01 22:30:23",
                 order_number: "20180701223023001",
                 content: "记得周六发货",
             },
             {
                 date: "2018-07-01 22:30:23",
                 order_number: "20180701223023001",
                 content: "记得周六发货",
             }
         ]
    
    '''
    list = []
    for mc in membercomments:
        temp_mc = {}
        temp_mc['date'] = mc.create_time.strftime('%Y-%m-%d')
        temp_mc['order_number'] = mc.pay_order_id
        temp_mc['content'] = mc.content
        list.append(temp_mc)
    resp['data']['list'] = list
    return jsonify(resp)


@api.route('/wode')
def wode():
    resp = {'code': 1, 'msg': '成功', 'data': {}}

    member = g.member

    if not member:
        resp['code'] = -1
        resp['msg'] = '验证失败'
        return jsonify(resp)

    members = Member.query.filter_by(id=member.id).all()

    # user_info: {
    #     nickname: "test",
    #     avatar_url: "/images/more/logo.png"
    # },
    user_info = {}
    for member in members:
        user_info['nickname'] = member.nickname
        user_info['avatar_url'] = member.avatar

    resp['data']['user_info'] = user_info
    return jsonify(resp)


@api.route('/show_address', methods=["GET", "POST"])
def show_address():
    resp = {'code': 1, 'msg': '成功', 'data': {}}

    member = g.member

    if not member:
        resp['code'] = -1
        resp['msg'] = '验证失败'
        return jsonify(resp)

    memberaddresses = MemberAddress.query.filter_by(member_id=member.id).all()
    addressList = []
    for address in memberaddresses:
        temp_address = {}
        temp_address['id'] = address.id
        temp_address['name'] = address.nickname
        temp_address['mobile'] = address.mobile
        temp_address['isDefault'] = address.is_default
        temp_address['detail'] = address.province_str + address.city_str + address.area_str + address.address
        addressList.append(temp_address)
    resp['data']['addressList'] = addressList

    return jsonify(resp)


#取消订单
@api.route('/cancel', methods=['POST'])
def cancel():
    resp = {'code': 1, 'msg': '成功', 'data': {}}

    member = g.member

    if not member:
        resp['code'] = -1
        resp['msg'] = '验证失败'
        return jsonify(resp)

    order_sn = request.form.get('order_sn')

    payorder = PayOrder.query.filter_by(member_id=member.id,order_sn=order_sn).first()
    if not payorder:
        resp['code'] = -1
        resp['msg'] = '订单不存在'
        return jsonify(resp)
    payorderitem = PayOrderItem.query.filter_by(pay_order_id=payorder.id,member_id=member.id).first()
    db.session.delete(payorderitem)
    db.session.commit()
    db.session.delete(payorder)
    db.session.commit()
    return jsonify(resp)
