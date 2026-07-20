"""
TakeoutSystem 外卖点餐系统 API 封装层

采用 API Object 模式，封装 11 个业务模块的全部接口。
每个业务 API 类继承自 BaseApi，通过构造方法注入 Token（AuthApi 和 HealthApi 除外）。

设计规范：
- 所有子类通过 super().__init__(base_url=config.API_BASE_URL) 初始化
- 除 AuthApi 和 HealthApi 外，其他类在 __init__ 中通过 session.headers 注入 Token
- 方法名与接口语义保持一致，参数名与 JSON 字段名映射清晰
- 所有方法返回原始 response 对象，不做断言（由测试层负责）
"""

import logging
from typing import Any, Dict, List, Optional

from api.base_api import BaseApi
from config.config import config

logger = logging.getLogger(__name__)


# ============================================================
# 工具函数
# ============================================================


def is_success(response) -> bool:
    """
    判断一次 API 调用是否业务成功。

    支持三种响应格式：
    1. 标准 Result 格式：{"code": 200, "success": true, ...}
    2. 健康检查格式：{"status": "UP", "checks": {...}}
    3. HTTP 状态码兜底：200 或 201

    Args:
        response: requests.Response 对象

    Returns:
        bool: 是否业务成功
    """
    if response.status_code not in (200, 201):
        return False
    try:
        body = response.json()
        # 标准 success 字段
        if "success" in body:
            return body["success"] is True
        # 健康检查格式
        if body.get("status") == "UP":
            return True
        # 兜底：有 code 字段且为 200
        if body.get("code") == 200:
            return True
        return False
    except Exception:
        return False


def get_biz_code(response) -> int:
    """
    提取响应中的业务状态码（区别于 HTTP 状态码）。

    如果 JSON 解析失败或缺少 code 字段，回退到 HTTP 状态码。

    Args:
        response: requests.Response 对象

    Returns:
        int: 业务状态码
    """
    try:
        return response.json().get("code", response.status_code)
    except Exception:
        return response.status_code


# ============================================================
# AuthApi — 认证模块（唯一不需要 Token 的 API 类）
# ============================================================


class AuthApi(BaseApi):
    """
    认证 API：登录、登出、Token 刷新

    注意：AuthApi 是唯一不需要 Token 的 API 类（登录前无 Token 可注入）。
    """

    def __init__(self, requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)

    def send_sms(self, phone: str) -> Dict[str, Any]:
        """
        发送短信验证码

        POST /api/auth/sms/send
        {"phone": phone}

        Args:
            phone: 手机号

        Returns:
            requests.Response 对象
        """
        logger.info(f"发送验证码: {phone}")
        return self.post("/api/auth/sms/send", json_data={"phone": phone})

    def login(self, phone: str, code: str) -> Dict[str, Any]:
        """
        登录

        POST /api/auth/login
        {"phone": phone, "code": code}

        成功返回 accessToken + refreshToken

        Args:
            phone: 手机号
            code: 验证码

        Returns:
            requests.Response 对象
        """
        logger.info(f"用户登录: {phone}")
        return self.post("/api/auth/login", json_data={"phone": phone, "code": code})

    def logout(self, refresh_token: str) -> Dict[str, Any]:
        """
        注销

        POST /api/auth/logout
        {"refreshToken": refresh_token}

        Args:
            refresh_token: 刷新令牌

        Returns:
            requests.Response 对象
        """
        logger.info("用户注销")
        return self.post("/api/auth/logout", json_data={"refreshToken": refresh_token})

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新 Token

        POST /api/auth/refresh
        {"refreshToken": refresh_token}

        Args:
            refresh_token: 刷新令牌

        Returns:
            requests.Response 对象
        """
        logger.info("刷新 Token")
        return self.post("/api/auth/refresh", json_data={"refreshToken": refresh_token})


# ============================================================
# UserApi — 用户模块（需 Token）
# ============================================================


class UserApi(BaseApi):
    """
    用户 API：个人资料、收货地址管理
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_profile(self) -> Dict[str, Any]:
        """
        获取当前登录用户信息

        GET /api/user/profile

        Returns:
            requests.Response 对象
        """
        logger.info("获取用户资料")
        return self.get("/api/user/profile")

    def update_profile(
        self, nickname: Optional[str] = None, avatar: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        更新用户资料

        PUT /api/user/profile

        Args:
            nickname: 昵称（可选）
            avatar: 头像 URL（可选）

        Returns:
            requests.Response 对象
        """
        data = {}
        if nickname is not None:
            data["nickname"] = nickname
        if avatar is not None:
            data["avatar"] = avatar
        logger.info(f"更新用户资料")
        return self.put("/api/user/profile", json_data=data)

    def list_addresses(self) -> Dict[str, Any]:
        """
        获取收货地址列表

        GET /api/user/address

        Returns:
            requests.Response 对象
        """
        logger.info("获取收货地址列表")
        return self.get("/api/user/address")

    def add_address(
        self,
        receiver: str,
        phone: str,
        province: str,
        city: str,
        district: str,
        detail: str,
        is_default: bool = False,
        longitude: float = 121.47,
        latitude: float = 31.23,
    ) -> Dict[str, Any]:
        """
        新增收货地址

        POST /api/user/address

        Args:
            receiver: 收件人
            phone: 联系电话
            province: 省份
            city: 城市
            district: 区县
            detail: 详细地址
            is_default: 是否默认地址
            longitude: 经度（默认上海坐标 121.47）
            latitude: 纬度（默认上海坐标 31.23）

        Returns:
            requests.Response 对象
        """
        data = {
            "receiver": receiver,
            "phone": phone,
            "province": province,
            "city": city,
            "district": district,
            "detail": detail,
            "isDefault": is_default,
            "longitude": longitude,
            "latitude": latitude,
        }
        logger.info(f"新增收货地址: {receiver}, {phone}")
        return self.post("/api/user/address", json_data=data)

    def update_address(self, address_id: int, **kwargs) -> Dict[str, Any]:
        """
        更新收货地址

        PUT /api/user/address/{id}

        Args:
            address_id: 地址 ID
            **kwargs: 可选更新字段（receiver/phone/province/city/district/detail/is_default 等）

        Returns:
            requests.Response 对象
        """
        logger.info(f"更新收货地址: {address_id}")
        return self.put(f"/api/user/address/{address_id}", json_data=kwargs)

    def delete_address(self, address_id: int) -> Dict[str, Any]:
        """
        删除收货地址

        DELETE /api/user/address/{id}

        Args:
            address_id: 地址 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"删除收货地址: {address_id}")
        return self.delete(f"/api/user/address/{address_id}")


# ============================================================
# MerchantApi — 商家模块（需 Token）
# ============================================================


class MerchantApi(BaseApi):
    """
    商家 API：搜索商家、查看详情、管理店铺信息

    同时服务于用户端（搜索/查看）和商家端（管理），通过传入不同的 Token 区分角色。
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_nearby(
        self, latitude: float = 31.23, longitude: float = 121.47, radius: int = 5000
    ) -> Dict[str, Any]:
        """
        获取附近商家列表

        GET /api/merchant/nearby

        Args:
            latitude: 纬度
            longitude: 经度
            radius: 搜索半径（米），默认 5000 米

        Returns:
            requests.Response 对象
        """
        params = {"latitude": latitude, "longitude": longitude, "radius": radius}
        logger.info(f"获取附近商家: ({latitude}, {longitude}), 半径={radius}m")
        return self.get("/api/merchant/nearby", params=params)

    def search(self, keyword: str) -> Dict[str, Any]:
        """
        关键字搜索商家

        GET /api/merchant/search

        Args:
            keyword: 搜索关键字

        Returns:
            requests.Response 对象
        """
        logger.info(f"搜索商家: {keyword}")
        return self.get("/api/merchant/search", params={"keyword": keyword})

    def get_detail(self, merchant_id: int) -> Dict[str, Any]:
        """
        获取商家详情

        GET /api/merchant/{id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"获取商家详情: {merchant_id}")
        return self.get(f"/api/merchant/{merchant_id}")

    def get_my_info(self) -> Dict[str, Any]:
        """
        商家端：获取本店信息

        GET /api/merchant/my

        Returns:
            requests.Response 对象
        """
        logger.info("获取本店信息")
        return self.get("/api/merchant/my")

    def update_my_info(self, **kwargs) -> Dict[str, Any]:
        """
        商家端：更新店铺信息

        PUT /api/merchant/my

        Args:
            **kwargs: 可选字段（name/description/address/phone 等）

        Returns:
            requests.Response 对象
        """
        logger.info("更新店铺信息")
        return self.put("/api/merchant/my", json_data=kwargs)

    def toggle_status(self, status: int) -> Dict[str, Any]:
        """
        商家端：切换营业状态

        PUT /api/merchant/my/status

        Args:
            status: 0=打烊，1=营业

        Returns:
            requests.Response 对象
        """
        logger.info(f"切换营业状态: {status}")
        return self.put("/api/merchant/my/status", json_data={"status": status})


# ============================================================
# ProductApi — 商品模块（需 Token）
# ============================================================


class ProductApi(BaseApi):
    """
    商品 API：菜单查询、分类浏览、菜品管理（商家端）
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_menu(self, merchant_id: int) -> Dict[str, Any]:
        """
        获取餐厅完整菜单（含分类和菜品）

        GET /api/product/menu/{id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"获取菜单: merchant_id={merchant_id}")
        return self.get(f"/api/product/menu/{merchant_id}")

    def list_categories(self, merchant_id: int) -> Dict[str, Any]:
        """
        获取菜品分类列表

        GET /api/product/category?merchantId={merchant_id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"获取菜品分类: merchant_id={merchant_id}")
        return self.get("/api/product/category", params={"merchantId": merchant_id})

    def list_dishes(self, merchant_id: int) -> Dict[str, Any]:
        """
        获取菜品列表

        GET /api/product/dish?merchantId={merchant_id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"获取菜品列表: merchant_id={merchant_id}")
        return self.get("/api/product/dish", params={"merchantId": merchant_id})

    def add_dish(self, **kwargs) -> Dict[str, Any]:
        """
        商家端：新增菜品

        POST /api/product/dish

        Args:
            **kwargs: 菜品信息（name/price/categoryId/description/image 等）

        Returns:
            requests.Response 对象
        """
        logger.info("新增菜品")
        return self.post("/api/product/dish", json_data=kwargs)

    def update_dish(self, dish_id: int, **kwargs) -> Dict[str, Any]:
        """
        商家端：更新菜品信息

        PUT /api/product/dish/{id}

        Args:
            dish_id: 菜品 ID
            **kwargs: 更新字段（name/price/categoryId/description 等）

        Returns:
            requests.Response 对象
        """
        logger.info(f"更新菜品: dish_id={dish_id}")
        return self.put(f"/api/product/dish/{dish_id}", json_data=kwargs)

    def toggle_dish_status(self, dish_id: int, status: int) -> Dict[str, Any]:
        """
        商家端：菜品上下架

        PUT /api/product/dish/{id}/status

        Args:
            dish_id: 菜品 ID
            status: 0=下架，1=上架

        Returns:
            requests.Response 对象
        """
        logger.info(f"切换菜品状态: dish_id={dish_id}, status={status}")
        return self.put(
            f"/api/product/dish/{dish_id}/status", json_data={"status": status}
        )


# ============================================================
# CartApi — 购物车模块（需 Token）
# ============================================================


class CartApi(BaseApi):
    """
    购物车 API：增删改查购物车条目
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_cart(self, merchant_id: int) -> Dict[str, Any]:
        """
        获取指定商家的购物车内容

        GET /api/cart/{merchant_id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"获取购物车: merchant_id={merchant_id}")
        return self.get(f"/api/cart/{merchant_id}")

    def add_item(
        self,
        dish_id: int,
        merchant_id: int,
        quantity: int = 1,
        spec_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        添加菜品到购物车

        POST /api/cart/add

        Args:
            dish_id: 菜品 ID
            merchant_id: 商家 ID
            quantity: 数量，默认 1
            spec_id: 规格 ID（可选）

        Returns:
            requests.Response 对象
        """
        data = {"dishId": dish_id, "merchantId": merchant_id, "quantity": quantity}
        if spec_id is not None:
            data["specId"] = spec_id
        logger.info(
            f"添加购物车: dish_id={dish_id}, merchant_id={merchant_id}, qty={quantity}"
        )
        return self.post("/api/cart/add", json_data=data)

    def update_item(self, cart_id: int, quantity: int) -> Dict[str, Any]:
        """
        更新购物车商品数量（quantity <= 0 则自动删除）

        PUT /api/cart/{cart_id}

        Args:
            cart_id: 购物车条目 ID
            quantity: 新数量

        Returns:
            requests.Response 对象
        """
        logger.info(f"更新购物车: cart_id={cart_id}, quantity={quantity}")
        return self.put(f"/api/cart/{cart_id}", json_data={"quantity": quantity})

    def remove_item(self, cart_id: int) -> Dict[str, Any]:
        """
        从购物车删除指定条目

        DELETE /api/cart/{cart_id}

        Args:
            cart_id: 购物车条目 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"删除购物车条目: cart_id={cart_id}")
        return self.delete(f"/api/cart/{cart_id}")

    def clear_cart(self, merchant_id: int) -> Dict[str, Any]:
        """
        清空指定商家购物车

        DELETE /api/cart/clear/{merchant_id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"清空购物车: merchant_id={merchant_id}")
        return self.delete(f"/api/cart/clear/{merchant_id}")


# ============================================================
# OrderApi — 订单模块（需 Token，用户端 + 商家端）
# ============================================================


class OrderApi(BaseApi):
    """
    订单 API：用户下单 + 商家订单管理

    通过传入不同的 Token 区分用户角色：
    - 消费者 Token → 用户端方法生效
    - 商家 Token → 商家端方法生效
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    # ---- 用户端 ----

    def submit_order(
        self,
        merchant_id: int,
        address_id: int,
        items: List[Dict],
        remark: Optional[str] = None,
        coupon_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        提交订单

        POST /api/order/submit

        Args:
            merchant_id: 商家 ID
            address_id: 收货地址 ID
            items: 商品列表，如 [{"dishId": 1, "quantity": 2}, {"dishId": 3, "quantity": 1}]
            remark: 订单备注（可选）
            coupon_id: 优惠券 ID（可选）

        Returns:
            requests.Response 对象
        """
        data = {
            "merchantId": merchant_id,
            "addressId": address_id,
            "items": items,
        }
        if remark is not None:
            data["remark"] = remark
        if coupon_id is not None:
            data["userCouponId"] = coupon_id
        logger.info(f"提交订单: merchant_id={merchant_id}, items_count={len(items)}")
        return self.post("/api/order/submit", json_data=data)

    def list_orders(
        self, status: Optional[int] = None, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """
        获取我的订单列表

        GET /api/order/list

        Args:
            status: 订单状态（可选）
            page: 页码，默认 1
            size: 每页条数，默认 10

        Returns:
            requests.Response 对象
        """
        params = {"page": page, "size": size}
        if status is not None:
            params["status"] = status
        logger.info(f"获取我的订单列表: page={page}, size={size}")
        return self.get("/api/order/list", params=params)

    def get_order_detail(self, order_no: str) -> Dict[str, Any]:
        """
        获取订单详情

        GET /api/order/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"获取订单详情: order_no={order_no}")
        return self.get(f"/api/order/{order_no}")

    def cancel_order(self, order_no: str) -> Dict[str, Any]:
        """
        取消订单

        POST /api/order/cancel/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"取消订单: order_no={order_no}")
        return self.post(f"/api/order/cancel/{order_no}")

    def confirm_receipt(self, order_no: str) -> Dict[str, Any]:
        """
        确认收货

        POST /api/order/receive/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"确认收货: order_no={order_no}")
        return self.post(f"/api/order/receive/{order_no}")

    # ---- 商家端 ----

    def merchant_list_orders(
        self,
        merchant_id: int = 1,
        status: Optional[int] = None,
        page: int = 1,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        商家获取订单列表

        GET /api/order/merchant/list?merchantId={merchant_id}

        Args:
            merchant_id: 商家 ID，默认 1
            status: 订单状态（可选）
            page: 页码，默认 1
            size: 每页条数，默认 10

        Returns:
            requests.Response 对象
        """
        params = {"merchantId": merchant_id, "page": page, "size": size}
        if status is not None:
            params["status"] = status
        logger.info(
            f"商家获取订单列表: merchant_id={merchant_id}, page={page}, size={size}"
        )
        return self.get("/api/order/merchant/list", params=params)

    def accept_order(self, order_no: str) -> Dict[str, Any]:
        """
        商家接单

        POST /api/order/merchant/accept/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"商家接单: order_no={order_no}")
        return self.post(f"/api/order/merchant/accept/{order_no}")

    def reject_order(self, order_no: str, reason: str) -> Dict[str, Any]:
        """
        商家拒单

        POST /api/order/merchant/reject/{order_no}

        Args:
            order_no: 订单编号
            reason: 拒单原因

        Returns:
            requests.Response 对象
        """
        logger.info(f"商家拒单: order_no={order_no}")
        return self.post(
            f"/api/order/merchant/reject/{order_no}", json_data={"reason": reason}
        )

    def mark_ready(self, order_no: str) -> Dict[str, Any]:
        """
        商家标记备餐完成

        POST /api/order/merchant/ready/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"标记备餐完成: order_no={order_no}")
        return self.post(f"/api/order/merchant/ready/{order_no}")

    def complete_order(self, order_no: str) -> Dict[str, Any]:
        """
        商家完成配送

        POST /api/order/merchant/complete/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"完成配送: order_no={order_no}")
        return self.post(f"/api/order/merchant/complete/{order_no}")


# ============================================================
# PayApi — 支付模块（需 Token）
# ============================================================


class PayApi(BaseApi):
    """
    支付 API：创建支付、查询状态、模拟支付回调
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def create_payment(self, order_no: str, pay_type: int = 1) -> Dict[str, Any]:
        """
        创建支付记录

        POST /api/pay/create

        Args:
            order_no: 订单编号
            pay_type: 支付方式（1=模拟支付，测试用）

        Returns:
            requests.Response 对象
        """
        logger.info(f"创建支付: order_no={order_no}, pay_type={pay_type}")
        return self.post(
            "/api/pay/create", json_data={"orderNo": order_no, "payType": pay_type}
        )

    def get_payment_status(self, order_no: str) -> Dict[str, Any]:
        """
        查询支付状态

        GET /api/pay/status/{order_no}

        Args:
            order_no: 订单编号

        Returns:
            requests.Response 对象
        """
        logger.info(f"查询支付状态: order_no={order_no}")
        return self.get(f"/api/pay/status/{order_no}")

    def mock_callback(self, payment_no: str) -> Dict[str, Any]:
        """
        模拟支付回调（测试专用）

        POST /api/pay/callback

        Args:
            payment_no: 支付流水号

        Returns:
            requests.Response 对象
        """
        logger.info(f"模拟支付回调: payment_no={payment_no}")
        return self.post(
            "/api/pay/callback",
            json_data={
                "paymentNo": payment_no,
                "success": True,
            },
        )


# ============================================================
# ReviewApi — 评价模块（需 Token）
# ============================================================


class ReviewApi(BaseApi):
    """
    评价 API：提交评价、查看商家评价
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def submit_review(
        self, order_no: str, score: int, content: str = ""
    ) -> Dict[str, Any]:
        """
        提交评价

        POST /api/review

        Args:
            order_no: 订单编号
            score: 评分（1-5 星）
            content: 评价内容

        Returns:
            requests.Response 对象
        """
        logger.info(f"提交评价: order_no={order_no}, score={score}")
        return self.post(
            "/api/review",
            json_data={
                "orderNo": order_no,
                "score": score,
                "content": content,
            },
        )

    def get_merchant_reviews(
        self, merchant_id: int, page: int = 1, size: int = 10
    ) -> Dict[str, Any]:
        """
        获取商家评价列表（公开）

        GET /api/review/merchant/{id}

        Args:
            merchant_id: 商家 ID
            page: 页码，默认 1
            size: 每页条数，默认 10

        Returns:
            requests.Response 对象
        """
        params = {"page": page, "size": size}
        logger.info(f"获取商家评价: merchant_id={merchant_id}")
        return self.get(f"/api/review/merchant/{merchant_id}", params=params)

    def get_my_reviews(self) -> Dict[str, Any]:
        """
        获取我发表的所有评价

        GET /api/review/my

        Returns:
            requests.Response 对象
        """
        logger.info("获取我的评价")
        return self.get("/api/review/my")


# ============================================================
# CouponApi — 优惠券模块（需 Token）
# ============================================================


class CouponApi(BaseApi):
    """
    优惠券 API：查看可领取优惠券、领取、查看已领取
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def list_coupons(self) -> Dict[str, Any]:
        """
        获取平台可领取的优惠券列表

        GET /api/coupon/available

        Returns:
            requests.Response 对象
        """
        logger.info("获取可领取优惠券列表")
        return self.get("/api/coupon/available")

    def claim_coupon(self, coupon_id: int) -> Dict[str, Any]:
        """
        领取指定优惠券

        POST /api/coupon/receive/{coupon_id}

        Args:
            coupon_id: 优惠券 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"领取优惠券: coupon_id={coupon_id}")
        return self.post(f"/api/coupon/receive/{coupon_id}")

    def my_coupons(self) -> Dict[str, Any]:
        """
        获取我已领取的优惠券

        GET /api/coupon/my

        Returns:
            requests.Response 对象
        """
        logger.info("获取我的优惠券")
        return self.get("/api/coupon/my")


# ============================================================
# FavoriteApi — 收藏模块（需 Token）
# ============================================================


class FavoriteApi(BaseApi):
    """
    收藏 API：收藏/取消收藏商家、查看收藏列表
    """

    def __init__(self, token: str = "", requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)
        if token:
            self.requests.session.headers.update({"Authorization": f"Bearer {token}"})

    def add_favorite(self, merchant_id: int) -> Dict[str, Any]:
        """
        收藏商家

        POST /api/favorite/{merchant_id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"收藏商家: merchant_id={merchant_id}")
        return self.post(f"/api/favorite/{merchant_id}")

    def remove_favorite(self, merchant_id: int) -> Dict[str, Any]:
        """
        取消收藏商家

        DELETE /api/favorite/{merchant_id}

        Args:
            merchant_id: 商家 ID

        Returns:
            requests.Response 对象
        """
        logger.info(f"取消收藏: merchant_id={merchant_id}")
        return self.delete(f"/api/favorite/{merchant_id}")

    def list_favorites(self) -> Dict[str, Any]:
        """
        获取我的收藏列表

        GET /api/favorite

        Returns:
            requests.Response 对象
        """
        logger.info("获取收藏列表")
        return self.get("/api/favorite")


# ============================================================
# HealthApi — 健康检查（无需 Token）
# ============================================================


class HealthApi(BaseApi):
    """
    健康检查 API：检查 MySQL + Redis 连接状态

    唯一没有认证需求的只读 API，通常在测试前置条件中使用。
    """

    def __init__(self, requests=None):
        super().__init__(base_url=config.API_BASE_URL, requests=requests)

    def check(self) -> Dict[str, Any]:
        """
        检查服务端健康状态（MySQL + Redis）

        GET /api/health

        Returns:
            requests.Response 对象
        """
        logger.info("健康检查")
        return self.get("/api/health")
