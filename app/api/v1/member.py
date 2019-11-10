from app.libs.redprint import RedPrint
from flask import request, jsonify,current_app
import requests
from app import db
from app.models.food import Food
from app.models.member import Member,OauthMemberBind
#导入随机字符
from app.service.memberService import memberService
api = RedPrint('member', description='会员模块')

@api.route('/login', methods=['POST'])
def login():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    nickName = request.form.get('nickName')
    avataUrl = request.form.get('avataUrl')
    gender = request.form.get('gender')
    code = request.form.get('code')
    print(nickName, avataUrl, gender, code)

    if len(code) < 1:
        res['code'] = -1
        res['msg'] = 'code有误'
        return jsonify(res)

    if not all([nickName,avataUrl,gender,code]):
        res['code'] = -1
        res['msg'] = '参数有误'
        return jsonify(res)

    # 获取open_id
    open_id =  memberService.getOpenid(code)
    if not open_id:
        res['code'] = -1
        res['msg'] = '获取open_id出错'
        return jsonify(res)


    #存数据库去重
    oauthMemberBind = OauthMemberBind.query.filter_by(openid=open_id).first()
    if not oauthMemberBind:
        member = Member()
        member.nickname = nickName
        member.avatar = avataUrl
        member.gender = gender
        member.salt = memberService.getSalt()

        db.session.add(member)
        db.session.commit()

        Oauth_member_bind = OauthMemberBind()
        Oauth_member_bind.openid = open_id
        Oauth_member_bind.client_type= 'wx'
        Oauth_member_bind.type = 1
        Oauth_member_bind.member_id = member.id

        db.session.add(Oauth_member_bind)
        db.session.commit()

    member =  Member.query.get(oauthMemberBind.member_id)
    #生成前端所需要的token
    token = "%s#%s"%(memberService.geneAuthCode(member),member.id)
    res['data']['token'] = token
    return jsonify(res)



@api.route('/cklogin',methods=['POST'])
def ckligin():
    res = {'code': 1, 'msg': '成功', 'data': {}}
    code = request.form.get('code')
    if len(code) < 1:
        res['code'] = -1
        res['msg'] = 'code有误'
        return jsonify(res)

    open_id = memberService.getOpenid(code)
    if not open_id:
        res['code'] = -1
        res['msg'] = '获取open_id出错'
        return jsonify(res)
    oauthMemberBind = OauthMemberBind.query.filter_by(openid=open_id).first()
    if not oauthMemberBind :
        res['code'] = -1
        res['msg'] = '用户不存在'
        return jsonify(res)
    #
    member =  Member.query.get(oauthMemberBind.member_id)
    #生成前端所需要的token
    token = "%s#%s"%(memberService.geneAuthCode(member),member.id)
    res['data']['token'] = token
    return jsonify(res)