//获取应用实例
var app = getApp();
Page({
    data: {
        "content": "非常愉快的订餐体验~~",
        "score": 10,
        "order_sn": ""
    },
    onLoad: function (e) {
        console.log(e, 'eeeeeesssssssssssssssssssssssssss');
        this.setData({
            "order_sn": e.id
        })
    },
    //接收输入框的内容
    inputchange: function (e) {
        this.setData({
            "content": e.detail.value
        })
    },
    scoreChange: function (e) {
        this.setData({
            "score": e.detail.value
        });
    },
    doComment: function () {
        var that = this;
        wx.request({
            method: "post",
            url: app.buildUrl("/v1/comment/add"),
            data: {
                'content': that.data.content,
                'score': that.data.score,
                'order_sn': that.data.order_sn
            },
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
            }
        });
        wx.navigateTo({
             url:'/pages/my/commentList',
        })
    },
});