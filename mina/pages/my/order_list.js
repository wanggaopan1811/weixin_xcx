var app = getApp();
Page({
    data: {
        statusType: ["待付款", "待发货", "待收货", "待评价", "已完成", "已关闭"],
        status: ["-8", "-7", "-6", "-5", "1", "0"],
        currentType: 0,
        tabClass: ["", "", "", "", "", ""]
    },
    statusTap: function (e) {
        // console.log(e,'sssssssssssssssssssssssssssss')
        var curType = e.currentTarget.dataset.index;
        this.data.currentType = curType;
        this.setData({
            currentType: curType
        });
        console.log(this.data.status[curType]);
        this.onShow();
        this.getorderLrist();
    },
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/pages/my/order_info"
        })
    },
    onLoad: function (options) {

        // 生命周期函数--监听页面加载
        this.getorderLrist()
    },
    onReady: function () {
        // 生命周期函数--监听页面初次渲染完
    },
    onShow: function () {
        var that = this;
        that.setData({
            order_list: [
                // {
                //     status: -8,
                //     status_desc: "待支付",
                //     date: "2018-07-01 22:30:23",
                //     order_number: "20180701223023001",
                //     note: "记得周六发货",
                //     total_price: "85.00",
                //     goods_list: [
                //         {
                //             pic_url: "/images/food.jpg"
                //         },
                //         {
                //             pic_url: "/images/food.jpg"
                //         }
                //     ]
                // }
            ]
        });
    },
    onHide: function () {
        // 生命周期函数--监听页面隐藏

    },
    onUnload: function () {
        // 生命周期函数--监听页面卸载

    },
    onPullDownRefresh: function () {
        // 页面相关事件处理函数--监听用户下拉动作

    },
    onReachBottom: function () {
        // 页面上拉触底事件的处理函数

    },
    getorderLrist: function () {
        var that = this;
        // console.log(this.data.order_list,'sssssssssssssssssssssssssssss')
        // console.log(that.data,'sssssssssssssssssssssssssssss')

        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/order/list',
            method: 'GET',
            data:{
                status:that.data.status[that.data.currentType]
            },
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data, '==============');
                if (res.data.code == -1) {
                    app.alert({
                        'content': res.data.msg
                    });
                    return
                }
                that.setData({
                        order_list: res.data.data.order_list,
                        // goods_list:res.data.data.order_list.goods_list
                    }
                )
            }
        });
    },
    //支付
    pay:function (e) {
        var order_sn = e.currentTarget.dataset.id
        var that = this
        wx.request({
            url: app.buildUrl('/v1/order/pay'),
            method: 'GET',
            data:{
            order_sn:order_sn
            },
            header: app.getRequestHeader(),
            success(res) {
                if (res.data.code != -1) {
                    app.alert({
                        'content': res.data.msg
                    });
                    return
                }
               wx.requestPayment({
                   'timeStamp':res.data.data.pay_info.timeStamp,
                   'nonceStr':res.data.data.pay_info.nonceStr,
                   'package':res.data.data.pay_info.package,
                   'SignType':'MD5',
                   'paySign':res.data.data.pay_info.paySign,
                   'success':function (res) {

                   },
                   'fail':function (res) {
                   },
                    'complete':function (res) {
                    }
               })
            }
        });
    },
    //取消订单
    cancel:function (e) {
        console.log(e,'wwwwwwwwwwwwwwwwwwwwwwwwwwww')
        var that = this;

        var order_sn = e.currentTarget.dataset.id;
        // console.log(order_sn,'oooooooooooooooooo')
        wx.request({
            url: "http://127.0.0.1:5000/api/v1/comment/cancel",
            // 'http://127.0.0.1:5000/api/v1/order/list',
            method: 'POST',

            data:{

                "order_sn":order_sn
            },

            header: app.getRequestHeader(),
            success(res) {
                if (res.data.code != -1) {
                    app.alert({
                        'content': res.data.msg
                    });
                    return
                }
                wx.redirectTo({
                    url: '/pages/my/order_list'
                })
            }
        });
    },

    goComment:function (e) {
        wx.navigateTo({
            // url:"/pages/my/comment",
             url:'/pages/my/comment?id='+e.currentTarget.dataset.id
        })
    }
    

});
