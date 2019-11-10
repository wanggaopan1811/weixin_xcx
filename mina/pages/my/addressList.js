//获取应用实例
var app = getApp();
Page({
    data: {
        addressList: []
    },
    selectTap: function (e) {
        //从商品详情下单选择地址之后返回
        wx.navigateBack({});
    },
    addessSet: function (e) {
        wx.navigateTo({
            url: "/pages/my/addressSet"
        })
    },
    onShow: function () {
        var that = this;
        that.setData({
            addressList: [
                {
                    id:1,
                    name: "test1",
                    mobile: "12345678901",
                    detail: "上海市浦东新区XX",
                    isDefault: 1
                },
                {
                    id: 2,
                    name: "test2",
                    mobile: "12345678901",
                    detail: "上海市浦东新区XX"
                }
            ]
        });
        that.show_address()
    },
    //收货收货地址
    show_address:function () {
        var that = this;
        wx.request({
            url: app.buildUrl('/v1/comment/show_address'),
            method: 'GET',
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data)
                if (res.data.code == -1) {
                    app.alert({
                        'content': res.data.msg
                    })
                    return
                }
                    that.setData({
                       addressList:res.data.data.addressList
                    })
                }
        })
    }
});
