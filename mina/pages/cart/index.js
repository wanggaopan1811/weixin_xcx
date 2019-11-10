//index.js
var app = getApp();
Page({
    data: {},
    onLoad: function () {

    },
    onShow: function () {
        this.getCartList();
    },
    //每项前面的选中框
    selectTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (index !== "" && index != null) {
            list[parseInt(index)].active = !list[parseInt(index)].active;
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
        }
    },
    //计算是否全选了
    allSelect: function () {
        var list = this.data.list;
        var allSelect = false;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (curItem.active) {
                allSelect = true;
            } else {
                allSelect = false;
                break;
            }
        }
        return allSelect;
    },
    //计算是否都没有选
    noSelect: function () {
        var list = this.data.list;
        var noSelect = 0;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            if (!curItem.active) {
                noSelect++;
            }
        }
        if (noSelect == list.length) {
            return true;
        } else {
            return false;
        }
    },
    //全选和全部选按钮
    bindAllSelect: function () {
        var currentAllSelect = this.data.allSelect;
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            list[i].active = !currentAllSelect;
        }
        this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list);
    },
    //加数量
    jiaBtnTap: function (e) {
        var that = this;
        var index = e.currentTarget.dataset.index;
        var list = that.data.list;
        wx.request({
            url: app.buildUrl('/v1/card/add'),
            method: 'POST',
            data: {
                'id': list[parseInt(index)].food_id,
                'num': 1,
                'fromtype': 1,
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
                    'content': res.data.msg
                })
                //concat和push的区别,
                //相应结果
                that.setData({
                    'info': res.data.data.info,
                    'buyNumMax': res.data.data.stock
                })
                // WxParse.wxParse('article','html',that.data.info.summary,that,)
            }
        })
        list[parseInt(index)].number++;
        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list);
    },
    //减数量
    jianBtnTap: function (e) {
        var index = e.currentTarget.dataset.index;
        var list = this.data.list;
        if (list[parseInt(index)].number > 1) {
            list[parseInt(index)].number--;
            var that = this;
            wx.request({
                url: app.buildUrl('/v1/card/add'),
                method: 'POST',
                data: {
                    'id': list[parseInt(index)].food_id,
                    'num': -1,
                    'fromtype': 1,
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
                        'content': res.data.msg
                    })
                    //concat和push的区别,
                    //相应结果
                    that.setData({
                        'info': res.data.data.info,
                        'buyNumMax': res.data.data.stock
                    })
                    // WxParse.wxParse('article','html',that.data.info.summary,that,)
                }
            })
            that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list);
        }
    },

    //编辑默认全不选
    editTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = false;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    //选中完成默认全选
    saveTap: function () {
        var list = this.data.list;
        for (var i = 0; i < list.length; i++) {
            var curItem = list[i];
            curItem.active = true;
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    },
    getSaveHide: function () {
        return this.data.saveHidden;
    },
    totalPrice: function () {
        var list = this.data.list;
        var totalPrice = 0.00;
        for (var i = 0; i < list.length; i++) {
            if (!list[i].active) {
                continue;
            }
            totalPrice = totalPrice + parseFloat(list[i].price) * parseFloat(list[i].number);
        }
        return totalPrice;
    },
    setPageData: function (saveHidden, total, allSelect, noSelect, list) {
        this.setData({
            list: list,
            saveHidden: saveHidden,
            totalPrice: total,
            allSelect: allSelect,
            noSelect: noSelect,
        });
    },
    //去结算
    toPayOrder: function () {

         var list = this.data.list;
         console.log(list,'lllllllllllllllllllllllllllllll')
        var cart_ids = [];
        list = list.filter(function (item){
            if (item.active) {
                cart_ids.push(item.food_id);
            }
            return !item.active;
        });
        wx.navigateTo({
            url: "/pages/order/index?ids=" + JSON.stringify(cart_ids)+'&type=1'
        });
    },
    //如果没有显示去光光按钮事件
    toIndexPage: function () {
        wx.switchTab({
            url: "/pages/food/index"
        });
    },
    //选中删除的数据
    deleteSelected: function () {
        var list = this.data.list;
        var cart_ids = [];
        list = list.filter(function (item) {
            if (item.active) {
                cart_ids.push(item.id);
            }
            return !item.active;
        });

        //发起网络请求
        //发起请求
        wx.request({
            url: app.buildUrl('/v1/card/delete'),
            // app.buildUrl('/v1/card/add'),
            method: 'POST',
            data: {
                'ids': JSON.stringify(cart_ids)
            },
            header: app.getRequestHeader(),
            success(res) {
                console.log(res.data);
                if (res.data.code == -1) {
                    app.alert({
                        'content': res.data.msg
                    });
                    return
                }
                // console.log(res.data.data.ids,'wwwwwwwwwwwwwwwwwwwwwww')
            }
        });
        //发送请求到后台删除数据
        this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);

    },
    // deleteSelected: function () {
    //     var that = this
    //     );
    // },
    // getCartList: function () {
    //         this.setData({
    //             list: [
    //             {
    //                 "id": 1080,
    // 				"food_id":"5",
    //                 "pic_url": "/images/food.jpg",
    //                 "name": "小鸡炖蘑菇-1",
    //                 "price": "85.00",
    //                 "active": true,
    //                 "number": 1
    //             },
    //             {
    //                 "id": 1081,
    // 				"food_id":"6",
    //                 "pic_url": "/images/food.jpg",
    //                 "name": "小鸡炖蘑菇-2",
    //                 "price": "85.00",
    //                 "active": true,
    //                 "number": 1
    //             }
    //         ],
    //         saveHidden: true,
    //         totalPrice: "85.00",
    //         allSelect: true,
    //         noSelect: false,
    //     });
    //     this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), this.data.list);
    // },
    //展示购物车列表的数据
    getCartList: function () {
        var that = this;
        wx.login({
            success(res) {
                if (res.code) {
                    //发起网络请求
                    //发起请求
                    wx.request({
                        url: 'http://127.0.0.1:5000/api/v1/card/list',
                        data: {
                            code: res.code,
                        },
                        method: 'GET',
                        header: app.getRequestHeader(),
                        success(res) {
                            console.log(res.data);
                            if (res.data.code == -1) {
                                app.alert({
                                    'content': res.data.msg
                                });
                                return
                            }
                            that.setData({
                                list: res.data.data.list,
                                totalPrice: res.data.data.totalPrice,
                                saveHidden: true,
                                allSelect: true,
                                noSelect: false,

                            })
                            // wx.switchTab({toPayOrder
                            //     url: '/pages/food/index',
                            // });
                            that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), that.data.list);
                        }
                    })
                } else {
                    console.log('登录失败！' + res.errMsg)
                }
            }
        });
    }
});
