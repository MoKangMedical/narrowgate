"""
窄门 (NarrowGate) - 统一支付系统

支持微信支付和支付宝
"""

import json
import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 微信支付SDK
try:
    from wechatpayv3 import WeChatPay, WeChatPayType
    WECHAT_PAY_AVAILABLE = True
except ImportError:
    WECHAT_PAY_AVAILABLE = False

# 支付宝SDK
try:
    from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
    from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
    ALIPAY_AVAILABLE = True
except ImportError as e:
    ALIPAY_AVAILABLE = False


class PaymentMethod(str, Enum):
    """支付方式"""
    WECHAT = "wechat"
    ALIPAY = "alipay"


class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentConfig:
    """支付配置"""
    # 微信支付配置
    wechat_mch_id: str = ""
    wechat_api_key: str = ""
    wechat_cert_path: str = ""
    wechat_key_path: str = ""
    wechat_app_id: str = ""
    wechat_notify_url: str = ""
    
    # 支付宝配置
    alipay_app_id: str = ""
    alipay_private_key: str = ""
    alipay_public_key: str = ""
    alipay_notify_url: str = ""
    
    # 通用配置
    currency: str = "CNY"
    expire_minutes: int = 30
    
    @classmethod
    def from_env(cls):
        """从环境变量创建配置"""
        return cls(
            wechat_mch_id=os.getenv("WECHAT_PAY_MCH_ID", ""),
            wechat_api_key=os.getenv("WECHAT_PAY_API_KEY", ""),
            wechat_cert_path=os.getenv("WECHAT_PAY_CERT_PATH", ""),
            wechat_key_path=os.getenv("WECHAT_PAY_KEY_PATH", ""),
            wechat_app_id=os.getenv("WECHAT_PAY_APP_ID", ""),
            wechat_notify_url=os.getenv("WECHAT_PAY_NOTIFY_URL", ""),
            alipay_app_id=os.getenv("ALI_PAY_APP_ID", ""),
            alipay_private_key=os.getenv("ALI_PAY_PRIVATE_KEY", ""),
            alipay_public_key=os.getenv("ALI_PAY_PUBLIC_KEY", ""),
            alipay_notify_url=os.getenv("ALI_PAY_NOTIFY_URL", ""),
            currency=os.getenv("PAYMENT_CURRENCY", "CNY"),
            expire_minutes=int(os.getenv("PAYMENT_EXPIRE_MINUTES", "30"))
        )


class PaymentManager:
    """支付管理器"""
    
    def __init__(self, db, config: PaymentConfig = None):
        self.db = db
        self.config = config or PaymentConfig()
        self._wechat_pay = None
        self._alipay_client = None
        self._init_clients()
    
    def _init_clients(self):
        """初始化支付客户端"""
        # 初始化微信支付
        if WECHAT_PAY_AVAILABLE and self.config.wechat_mch_id:
            try:
                self._wechat_pay = WeChatPay(
                    wechatpay_type=WeChatPayType.NATIVE,
                    mchid=self.config.wechat_mch_id,
                    private_key=self.config.wechat_api_key,
                    cert_serial_no=self.config.wechat_cert_path,
                    apiv3_key=self.config.wechat_key_path,
                    appid=self.config.wechat_app_id,
                    notify_url=self.config.wechat_notify_url
                )
            except Exception as e:
                print(f"微信支付客户端初始化失败: {e}")
        
        # 初始化支付宝
        if ALIPAY_AVAILABLE and self.config.alipay_app_id:
            try:
                alipay_config = AlipayClientConfig()
                alipay_config.app_id = self.config.alipay_app_id
                alipay_config.app_private_key = self.config.alipay_private_key
                alipay_config.alipay_public_key = self.config.alipay_public_key
                alipay_config.sign_type = "RSA2"
                self._alipay_client = DefaultAlipayClient(alipay_config)
            except Exception as e:
                print(f"支付宝客户端初始化失败: {e}")
    
    def create_order(self, user_id: str, amount: float, payment_method: str, 
                    description: str = "窄门高级会员") -> Dict[str, Any]:
        """创建支付订单"""
        order_id = f"order_{uuid.uuid4().hex[:16]}"
        now = datetime.now().isoformat()
        
        # 保存订单到数据库
        with self.db._connect() as conn:
            conn.execute(
                """INSERT INTO payment_orders 
                (id, user_id, amount, payment_method, status, created_at, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (order_id, user_id, amount, payment_method, PaymentStatus.PENDING, now, description)
            )
        
        # 根据支付方式创建支付
        if payment_method == PaymentMethod.WECHAT:
            return self._create_wechat_order(order_id, amount, description)
        elif payment_method == PaymentMethod.ALIPAY:
            return self._create_alipay_order(order_id, amount, description)
        else:
            return {"success": False, "error": "不支持的支付方式"}
    
    def _create_wechat_order(self, order_id: str, amount: float, description: str) -> Dict[str, Any]:
        """创建微信支付订单"""
        if not self._wechat_pay:
            return {"success": False, "error": "微信支付未配置"}
        
        try:
            amount_cents = int(amount * 100)
            result = self._wechat_pay.pay(
                description=description,
                out_trade_no=order_id,
                amount={'total': amount_cents, 'currency': self.config.currency},
                pay_type=WeChatPayType.NATIVE
            )
            
            if result.get('code_url'):
                with self.db._connect() as conn:
                    conn.execute(
                        "UPDATE payment_orders SET trade_no = ? WHERE id = ?",
                        (result.get('prepay_id'), order_id)
                    )
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "payment_url": result.get('code_url'),
                    "prepay_id": result.get('prepay_id')
                }
            else:
                return {"success": False, "error": "创建微信支付订单失败"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_alipay_order(self, order_id: str, amount: float, description: str) -> Dict[str, Any]:
        """创建支付宝订单"""
        return {"success": False, "error": "支付宝功能暂时不可用，请使用微信支付"}
    
    def handle_wechat_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理微信支付回调"""
        try:
            if not self._wechat_pay.callback_verify(callback_data):
                return {"success": False, "error": "签名验证失败"}
            
            order_id = callback_data.get('out_trade_no')
            trade_no = callback_data.get('transaction_id')
            
            with self.db._connect() as conn:
                conn.execute(
                    """UPDATE payment_orders 
                    SET status = ?, trade_no = ?, paid_at = ? 
                    WHERE id = ?""",
                    (PaymentStatus.PAID, trade_no, datetime.now().isoformat(), order_id)
                )
                
                order = conn.execute(
                    "SELECT user_id FROM payment_orders WHERE id = ?",
                    (order_id,)
                ).fetchone()
                
                if order:
                    user_id = order['user_id']
                    conn.execute(
                        """UPDATE users 
                        SET subscription_type = 'premium', 
                            subscription_expires = datetime('now', '+30 days')
                        WHERE id = ?""",
                        (user_id,)
                    )
            
            return {"success": True, "order_id": order_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def handle_alipay_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理支付宝回调"""
        try:
            order_id = callback_data.get('out_trade_no')
            trade_no = callback_data.get('trade_no')
            
            with self.db._connect() as conn:
                conn.execute(
                    """UPDATE payment_orders 
                    SET status = ?, trade_no = ?, paid_at = ? 
                    WHERE id = ?""",
                    (PaymentStatus.PAID, trade_no, datetime.now().isoformat(), order_id)
                )
                
                order = conn.execute(
                    "SELECT user_id FROM payment_orders WHERE id = ?",
                    (order_id,)
                ).fetchone()
                
                if order:
                    user_id = order['user_id']
                    conn.execute(
                        """UPDATE users 
                        SET subscription_type = 'premium', 
                            subscription_expires = datetime('now', '+30 days')
                        WHERE id = ?""",
                        (user_id,)
                    )
            
            return {"success": True, "order_id": order_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """获取订单状态"""
        with self.db._connect() as conn:
            order = conn.execute(
                "SELECT * FROM payment_orders WHERE id = ?",
                (order_id,)
            ).fetchone()
            
            if order:
                return dict(order)
            return None
    
    def get_user_orders(self, user_id: str, limit: int = 50) -> list:
        """获取用户订单列表"""
        with self.db._connect() as conn:
            orders = conn.execute(
                "SELECT * FROM payment_orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            
            return [dict(order) for order in orders]
    
    def refund_order(self, order_id: str, reason: str = "用户申请退款") -> Dict[str, Any]:
        """退款"""
        try:
            with self.db._connect() as conn:
                order = conn.execute(
                    "SELECT * FROM payment_orders WHERE id = ?",
                    (order_id,)
                ).fetchone()
                
                if not order:
                    return {"success": False, "error": "订单不存在"}
                
                if order['status'] != PaymentStatus.PAID:
                    return {"success": False, "error": "订单状态不正确"}
                
                conn.execute(
                    """UPDATE payment_orders 
                    SET status = ?, refund_reason = ?, refunded_at = ? 
                    WHERE id = ?""",
                    (PaymentStatus.REFUNDED, reason, datetime.now().isoformat(), order_id)
                )
                
                user_id = order['user_id']
                conn.execute(
                    """UPDATE users 
                    SET subscription_type = 'free', 
                        subscription_expires = NULL
                    WHERE id = ?""",
                    (user_id,)
                )
            
            return {"success": True, "order_id": order_id}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


def create_payment_routes(app, db, config: PaymentConfig = None):
    """创建支付路由"""
    from fastapi import HTTPException, Request
    
    payment_manager = PaymentManager(db, config)
    
    @app.post("/api/payment/create")
    async def create_payment(request: Request):
        """创建支付订单"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            amount = data.get('amount')
            payment_method = data.get('payment_method')
            description = data.get('description', '窄门高级会员')
            
            if not all([user_id, amount, payment_method]):
                raise HTTPException(status_code=400, detail="缺少必要参数")
            
            result = payment_manager.create_order(user_id, amount, payment_method, description)
            
            if result.get('success'):
                return result
            else:
                raise HTTPException(status_code=400, detail=result.get('error', '创建订单失败'))
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/payment/wechat/notify")
    async def wechat_notify(request: Request):
        """微信支付回调"""
        try:
            data = await request.json()
            result = payment_manager.handle_wechat_callback(data)
            
            if result.get('success'):
                return {"code": "SUCCESS", "message": "成功"}
            else:
                return {"code": "FAIL", "message": result.get('error', '处理失败')}
                
        except Exception as e:
            return {"code": "FAIL", "message": str(e)}
    
    @app.post("/api/payment/alipay/notify")
    async def alipay_notify(request: Request):
        """支付宝回调"""
        try:
            data = await request.form()
            result = payment_manager.handle_alipay_callback(dict(data))
            
            if result.get('success'):
                return "success"
            else:
                return "fail"
                
        except Exception as e:
            return "fail"
    
    @app.get("/api/payment/status/{order_id}")
    async def get_payment_status(order_id: str):
        """获取支付状态"""
        try:
            result = payment_manager.get_order_status(order_id)
            
            if result:
                return result
            else:
                raise HTTPException(status_code=404, detail="订单不存在")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/payment/user/{user_id}")
    async def get_user_payments(user_id: str):
        """获取用户支付记录"""
        try:
            result = payment_manager.get_user_orders(user_id)
            return {"orders": result}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/payment/refund/{order_id}")
    async def refund_payment(order_id: str, request: Request):
        """退款"""
        try:
            data = await request.json()
            reason = data.get('reason', '用户申请退款')
            
            result = payment_manager.refund_order(order_id, reason)
            
            if result.get('success'):
                return result
            else:
                raise HTTPException(status_code=400, detail=result.get('error', '退款失败'))
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return payment_manager