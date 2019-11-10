var app = getApp();
Page({
    data: {
        statusType: ["待付款", "待发货", "待收货", "待评价", "已完成","已关闭"],
        status:[ "-8","-7","-6","-5","1","0" ],
        currentType: 0,
        tabClass: ["", "", "", "", "", ""]
    },
    statusTap: function (e) {
        var curType = e.currentTarget.dataset.index;
        this.data.currentType = curType;
        this.setData({
            currentType: curType
        });
        this.onShow();
    },
    orderDetail: function (e) {
        wx.redirectTo({
            url: "/pages/my/order_info"
        })
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载
    },
    onReady: function () {
        // 生命周期函数--监听页面初次渲染完
    },
    onShow: function () {
        var that = this;
        that.setData({
            // order_list: [
            //     {
			// 		status: -8,
            //         status_desc: "待支付",
            //         date: "2018-07-01 22:30:23",
            //         order_number: "20180701223023001",
            //         note: "记得周六发货",
            //         total_price: "85.00",
            //         goods_list: [
            //             {
            //                 pic_url: "/images/food.jpg"
            //             },
            //             {
            //                 pic_url: "/images/food.jpg"
            //             }
            //         ]
            //     }
            // ]
        });
        this.getOrderList()
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
    getorderLirst:function () {
        var that = this;
        wx.request({
            url:app.buildUrl('/v1/order/list'),
            method:'GET',
            data: {
                'status':that.data.status[this.data.currentType]
            },

            header:app.getRequestHeader(),
            success(res) {
                if(res.data.code == -1){
                    // app.alter({'content':res.data.msg})
                    // return
                }
                that.setData({
                    order_list:res.data.data.order_list,
                })
            }
        })
    },
    pay: function (e) {
        var order_sn = e.currentTarget.dataset.id
        var that = this;
        wx.request({
            url: app.buildUrl('/v1/order/pay'),
            method: 'GET',
            header: app.getRequestHeader(),
            data: {
                'order_sn': order_sn
            },
            success(res) {
                var data = res.data
                if (res.data.code == -1) {
                    app.alter({'content': res.data.msg})
                    return
                }
                wx.requestPayment(
                    {
                        'timeStamp': res.data.data.pay_info.timeStamp,
                        'nonceStr': res.data.data.pay_info.nonceStr,
                        'package': res.data.data.pay_info.package,
                        'signType': 'MD5',
                        'paySign': res.data.data.pay_info.paySign,
                        'success': function (res) {
                        },
                        'fail': function (res) {
                        },
                        'complete': function (res) {
                        }
                    })
            }
        })
    },
    goComment:function (e) {
        wx.navigateTo({
            url:'/pages/my/comment?id='+e.currentTarget.dataset.id
        })
    },
    deleteaddress:function (e) {
        var list = this.data.list;
        var food_ids = [];
        list = list.filter(function ( item ) {
            if(item.active ){
                cart_ids.push( item.food_id );
            }
            return !item.active;
        });
        this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        //发送请求到后台删除数据
        var that=this
        wx.request({
            url:app.buildUrl('/v1/order/delete'),
            method:'POST',
            data:{
                ids:JSON.stringify(cart_ids)
            },
            header:app.getRequestHeader(),
            success(res) {
                if (res.data.code == 1) {

                    // that.setData({
                    //     banners:res.data.data.banners,
                    //     categories:res.data.data.categories,
                    // })
                }
            }
        })
    }
})
