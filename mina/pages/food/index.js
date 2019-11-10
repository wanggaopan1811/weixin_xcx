//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        page: 1,
        ismore: 1,
        isloading: false
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });

        // that.setData({
        // banners: [
        //     {
        //         "id": 1,
        //         "pic_url": "/images/food.jpg"
        //     },
        //     {
        //         "id": 2,
        //         "pic_url": "/images/food.jpg"
        //     },
        //     {
        //         "id": 3,
        //         "pic_url": "/images/food.jpg"
        //     }
        // ],
        // categories: [
        //     {id: 0, name: "全部"},
        //     {id: 1, name: "川菜"},
        //     {id: 2, name: "东北菜"},
        // ],
        // activeCategoryId: 0,
        // goods: [
        //     {
        //         "id": 1,
        //         "name": "小鸡炖蘑菇-1",
        //         "min_price": "15.00",
        //         "price": "15.00",
        //         "pic_url": "/images/food.jpg"
        //     },
        //     {
        //         "id": 2,
        //         "name": "小鸡炖蘑菇-1",
        //         "min_price": "15.00",
        //         "price": "15.00",
        //         "pic_url": "/images/food.jpg"
        //     },
        //     {
        //         "id": 3,
        //         "name": "小鸡炖蘑菇-1",
        //         "min_price": "15.00",
        //         "price": "15.00",
        //         "pic_url": "/images/food.jpg"
        //     },
        //     {
        //         "id": 4,
        //         "name": "小鸡炖蘑菇-1",
        //         "min_price": "15.00",
        //         "price": "15.00",
        //         "pic_url": "/images/food.jpg"
        //     }
        //
        // ],
        //     loadingMoreHidden: false
        // });
        that.getFoodAndCaracty();
        that.getFood()
    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    listenerSearchInput: function (e) {
        this.setData({
            searchInput: e.detail.value
        });
    },
    toSearch: function (e) {
        this.setData({
            p: 1,
            goods: [],
            loadingMoreHidden: true
        });
        this.getFoodList();
    },
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        console.log(e, '2365666666666666')
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    //下拉展示数据
    onReachBottom: function () {
        console.log('到底了')
        var that = this
        //当isloading是false的时候
        if (that.data.isloading == false) {

            if (that.data.ismore != 0) {
                that.setData({
                    page: that.data.page + 1
                })//调用函数
                that.getFood()
            }
        }
    },
    //点击
    cateclick: function (e) {
        var that = this
        console.log(e.target.id)
        that.setData({
            activeCategoryId: e.target.id,
            goods: [],
            page: 1
        })
        //点击分类重新获取数据
        that.getFood()
    },
    //发起请求
    getFoodAndCaracty: function (e) {
        var that = this
        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/food/foods',
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
                        banners: res.data.data.banners,
                        categories: res.data.data.categories
                    })
                }
        })
    },
    //发起请求
    getFood: function (e) {

        var that = this

        that.setData({
            'isloading': true
        })
        // if (that.data.ismore == 0){
        //     return
        // }
        wx.request({
            url: 'http://127.0.0.1:5000/api/v1/food/zhanshi',
            method: 'GET',
            data: {
                'cid': that.data.activeCategoryId,
                'page': that.data.page
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
                    //concat和push的区别,
                    //相应结果
                    that.setData({
                        goods: that.data.goods.concat(res.data.data.goods),
                        'ismore': res.data.data.ismore,
                        'isloading': false
                    })
                    if (that.data.ismore == 0) {
                        that.setData({
                            loadingHidden: false
                        })
                    }
            }
        })
    }
});
