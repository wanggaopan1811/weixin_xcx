//app.js
App({
    onLaunch: function () {
    },
    globalData: {
        userInfo: null,
        version: "1.0",
        shopName: "Python3 + Flask 订餐全栈系统",
        domain: "http://127.0.0.1:5000/api"
    },
    tip: function (params) {
        var that = this;
        var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
        var content = params.hasOwnProperty('content') ? params['content'] : '';
        wx.showModal({
            title: title,
            content: content,
            success: function (res) {

                if (res.confirm) {//点击确定
                    if (params.hasOwnProperty('cb_confirm') && typeof (params.cb_confirm) == "function") {
                        params.cb_confirm();
                    }
                } else {//点击否
                    if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    alert: function (params) {
        var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
        var content = params.hasOwnProperty('content') ? params['content'] : '';
        wx.showModal({
            title: title,
            content: content,
            showCancel: false,
            success: function (res) {
                if (res.confirm) {//用户点击确定
                    if (params.hasOwnProperty('cb_confirm') && typeof (params.cb_confirm) == "function") {
                        params.cb_confirm();
                    }
                } else {
                    if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    console: function (msg) {
        console.log(msg);
    },
    getRequestHeader: function () {
        // var that = this;
        return {
            'content-type': 'application/x-www-form-urlencoded',
            'token': this.getToken('token'),

        }
    },
    setToken: function (key, token) {
        wx.setStorage({
            key: key,
            data: token
        })
    },
    buildUrl: function (path, params) {
        var url = this.globalData.domain + path;
        var _paramUrl = "";
        if (params) {
            _paramUrl = Object.keys(params).map(function (k) {
                return [encodeURIComponent(k), encodeURIComponent(params[k])].join("=");
            }).join("&");
            _paramUrl = "?" + _paramUrl;
        }
        return url + _paramUrl;
        },


    getToken: function (key) {
            try {
                var value = wx.getStorageSync(key);
                if (value) {
                    return value
                    // console.log(value,'-------------------')
                }
            } catch (e) {
                return ''
            }
        },
});