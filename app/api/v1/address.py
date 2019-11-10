from app.libs.redprint import RedPrint
import re
from flask import jsonify, request, g, json
from app.models.address import MemberAddress
from app.service.memberService import memberService
from app.utils.common import ww
from app.service.cardService import cardService
from app import db

api = RedPrint('address', description='地址模块')


@api.route('/add', methods=['POST'])
def add():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    member = g.member
    if not member:
        res['code'] = -1
        res['msg'] = "用户不存"
        return jsonify(res)
    nickname = request.form.get('nickname')
    mobile = request.form.get('mobile')
    province_id = request.form.get('province_id')
    province_str = request.form.get('province_str')
    city_id = request.form.get('city_id')
    city_str = request.form.get('city_str')
    area_id = request.form.get('area_id')
    area_str = request.form.get('area_str')
    address = request.form.get('address')
    # 验证手机号
    mobile = str(mobile)
    zze = re.compile(r'1[35867]\d{9}')
    ze = zze.search(mobile)
    if ze == None:
        res["code"] = -1
        res["msg"] = "错误"

    count = MemberAddress.query.filter_by(is_default=1).count()
    memberAddress = MemberAddress()
    memberAddress.nickname = nickname
    memberAddress.mobile = mobile
    memberAddress.province_str = province_str
    memberAddress.province_id = province_id
    memberAddress.city_id = city_id
    memberAddress.city_str = city_str
    memberAddress.area_id = area_id
    memberAddress.area_str = area_str
    memberAddress.address = address
    memberAddress.member_id = member.id
    if count == 0:
        memberAddress.is_default = 1
    else:
        memberAddress.is_default = 0
    db.session.add(memberAddress)
    db.session.commit()
    return jsonify(res)
