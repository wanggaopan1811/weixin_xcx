//获取应用实例
var app = getApp();

Page({
    data: {
        ids: [],
        address_id: 0,
        note: '',
        order_list: '',
        num: 1,
        type: 0,
        goods_list: [
            // {
            //     id: 22,
            //     name: "小鸡炖蘑菇",
            //     price: "85.00",
            //     pic_url: "/images/food.jpg",
            //     number: 1,
            // },
            // {
            //     id: 22,
            //     name: "小鸡炖蘑菇",
            //     price: "85.00",
            //     pic_url: "/images/food.jpg",
            //     number: 1,
            // }
        ],
        default_address: {
            // name: "编程浪子",
            // mobile: "12345678901",
            // detail: "上海市浦东新区XX",
        },
        yun_price: "1.00",
        pay_price: "85.00",
        total_price: "86.00",
        params: null
    },
    //接收传过来的ids
    onShow: function () {
        var that = this;
        that.setData({})
    },
    onLoad: function (e) {
        // var ids = JSON.parse(e.ids);
        var that = this;
        //为了区分从哪里来的
        that.setData({
            type: e.type
        });
        //从立即购买
        if (that.data.type == 1) {
            that.setData({
                ids: JSON.parse(e.ids),
                num: e.num
            })
        }
        //不管从购物车还是立即购买，都执行
        that.setData({
            ids: JSON.parse(e.ids),
        });
        that.getOrderIndex();
    },
    getInput: function (e) {
        this.setData({
            note: e.detail.value
        })
    },
    //提交并传数据
    createOrder: function (e) {
        var that = this;
        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/order/create',
            data: {
                'ids': JSON.stringify(that.data.ids),
                'address_id': that.data.address_id,
                'note': that.data.note
            },
            method: 'POST',
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data)
                if (res.data.code == -1) {
                    app.alert({
                        'content': res.data.msg
                    })
                    return
                }
                //重定向
                wx.redirectTo({
                    url: '/page/my/order_list'
                });
            }
        });
        wx.navigateTo({
            url: "/pages/my/order_list",
        });

    },
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },
    getOrderIndex: function () {
        var that = this;
        if (that.data.type == 0) {
            var data = {
                'ids': JSON.stringify(that.data.ids),
                'type': that.data.type
            }
        } else {
            var data = {
                'ids': JSON.stringify(that.data.ids),
                'num': that.data.num,
                'type': that.data.type

            }
        }
        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/order/commit',
            method: 'POST',
            data: {
                'ids': JSON.stringify(that.data.ids),
                'num': that.data.num,
                'type': that.data.type

            },
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data, 'wwwwwwwwdddddddd');
                if (res.data.code == -1) {
                    app.alert({
                        'content': res.data.msg
                    });
                    return
                }
                that.setData({
                        goods_list: res.data.data.goods_list,
                        default_address: res.data.data.default_address,
                        yun_price: "0.00",
                        pay_price: res.data.data.total_price,
                        total_price: res.data.data.total_price,
                        params: null,
                        address_id: res.data.data.default_address.id,
                    }
                )
            }
        });
    },

});
