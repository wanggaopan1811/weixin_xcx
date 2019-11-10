//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax:1,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 4,
        commentCount:2,
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            "id": e.id,
            // "info": {
            //     "name": "小鸡炖蘑菇",
            //     "summary": '<p>多色可选的马甲</p><p><img src="http://www.timeface.cn/uploads/times/2015/07/071031_f5Viwp.jpg"/></p><p><br/>相当好吃了</p>',
            //     "total_count": 2,
            //     "comment_count": 2,
            //     "stock": 2,
            //     "price": "80.00",
            //     "main_image": "/images/food.jpg",
            //     "pics": [ '/images/food.jpg','/images/food.jpg' ]
            // },
            //购买的最大量
            // buyNumMax:2,
            commentList: [
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                },
                {
                    "score": "好评",
                    "date": "2017-10-11 10:20:00",
                    "content": "非常好吃，一直在他们加购买",
                    "user": {
                        "avatar_url": "/images/more/logo.png",
                        "nick": "angellee 🐰 🐒"
                    }
                }
            ]
        });

        // WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);

        that.getFoodinfo()
    },
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    //添加购物车
    addShopCar: function () {
        var that = this
        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/card/add',
            method: 'POST',
            data:{
                'id':that.data.id,
                'num':that.data.buyNumber,
                'fromtype':0,
                // 'token':app.getToken('token'),
            },
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data)
                 if (res.data.code == -1) {
                                app.alert({
                                    'content': res.data.msg
                                })
                                return
                            }
                    app.alert({
                        'content':res.data.msg
                    })
                    that.closePopupTap()
                    //concat和push的区别,
                    //相应结果
                    that.setData({
                        'info':res.data.data.info,
                        'buyNumMax':res.data.data.stock
                    })
                    // WxParse.wxParse('article','html',that.data.info.summary,that,)
                    }
        })
    },
    //立即购买
    buyNow: function () {
        wx.navigateTo({
            url: "/pages/order/index?ids="+JSON.stringify([this.data.id])+ '&num='+this.data.buyNumber+'&type=1'
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        })
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if( this.data.buyNumber <= this.data.buyNumMin){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if( this.data.buyNumber >= this.data.buyNumMax ){
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    // 根据id发起请求，获取页面
    getFoodinfo: function () {
        var that = this
        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/food/info',
            method: 'GET',
            data:{
                'id':that.data.id
            },
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data.data.info)
                if (res.data.code == 1) {
                    //concat和push的区别,
                    //相应结果
                    that.setData({
                        'info':res.data.data.info,
                        'buyNumMax':res.data.data.info.stock
                    })
                    WxParse.wxParse('article','html',that.data.info.summary,that,)
                    }
                }

        })
    }
});
