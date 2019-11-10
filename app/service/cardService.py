import random
import string
import hashlib
from flask import current_app
import requests
from app.models.food import Food
from app.models.cart import MemberCart
from app.utils.common import ww
from app import db

# 随机字符串
class cardService():

    @staticmethod
    def addCard(member, id, num):
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


    @staticmethod
    def list(member):
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

        return list,totalPrice