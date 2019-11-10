var app = getApp();
Page({
    data: {
        // list: [
            // {
            //     date: "2018-07-01 22:30:23",
            //     order_number: "20180701223023001",
            //     content: "记得周六发货",
            // },
            // {
            //     date: "2018-07-01 22:30:23",
            //     order_number: "20180701223023001",
            //     content: "记得周六发货",
            // }
        // ]
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载

    },
    onShow: function () {
        var that = this;
        that.list1()
    },

    list1: function () {
        var that = this;
        wx.request({
            method: "GET",
            url: app.buildUrl("/v1/comment/list1"),

            // data: {
            // },
            header: app.getRequestHeader(),
            success: function (resp) {
                if (resp.code != 200) {
                    // app.alert({"content": resp.msg});
                    // return;
                }
                that.setData({
                    // "date":res.data.list.date,
                    // "order_number":res.data.data.list.order_number,
                    // "content":res.data.data.list.content,
                    list:resp.data.data.list
                })
            }
        });
        // wx.navigateTo({
        //      url:'/pages/my/commentList',
        // })
    },
});
