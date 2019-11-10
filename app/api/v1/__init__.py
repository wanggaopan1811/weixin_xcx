from flask import Blueprint
from . import user,member,food,info,card,address,order,comment


def createBluePrint():
    bp = Blueprint('v1', __name__)
    user.api.register(bp)
    member.api.register(bp)
    food.api.register(bp)
    info.api.register(bp)
    card.api.register(bp)
    address.api.register(bp)
    order.api.register(bp)
    comment.api.register(bp)
    return bp
