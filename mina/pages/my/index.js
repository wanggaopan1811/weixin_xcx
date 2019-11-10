//获取应用实例
var app = getApp();
Page({
    data: {},
    onLoad() {
        // this.wode();
    },
    onShow() {
        var that = this;

        that.setData({
            // user_info: {
            //     nickname: "test",
            //     avatar_url: "/images/more/logo.png"
            // },
        });
        that.wode();
    },
    wode:function () {
        var that = this
        wx.request({
            url: app.buildUrl('/v1/comment/wode'),
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
                       user_info:res.data.data.user_info
                    })
                }
        })
    }
});