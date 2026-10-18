# -*- coding: utf-8 -*-
"""Abandoned Checkout Dynamic Incentive Negotiator Skill for GenPark Agentic Commerce."""
import json
import math
from typing import Dict, Any

def evaluate_abandoned_cart_incentive(cart_value_usd: float, product_margin_pct: float, customer_ltv_usd: float, abandonment_minutes_elapsed: float) -> Dict[str, Any]:
    # Constraint checks
    if cart_value_usd <= 0.0 or product_margin_pct <= 0.0:
        return {"error": "Invalid cart value or margin bounds"}

    # Base rule: Maximum allowable incentive is 40% of net margin
    max_incentive_pct = round(product_margin_pct * 0.40, 1)

    # Customer VIP tier multiplier
    if customer_ltv_usd > 1500.0:
        ltv_multiplier = 1.0
        customer_tier = "PLATINUM_VIP"
    elif customer_ltv_usd > 500.0:
        ltv_multiplier = 0.8
        customer_tier = "GOLD_MEMBER"
    elif customer_ltv_usd > 100.0:
        ltv_multiplier = 0.6
        customer_tier = "SILVER_REGULAR"
    else:
        ltv_multiplier = 0.4
        customer_tier = "FIRST_TIME_PROSPECT"

    # Urgency urgency escalation based on abandonment latency
    if abandonment_minutes_elapsed < 30.0:
        urgency_factor = 0.5  # Soft nudge, don't burn margin too early
        strategy = "FREE_EXPEDITED_SHIPPING_NUDGE"
    elif abandonment_minutes_elapsed <= 180.0:
        urgency_factor = 0.85 # Prime recovery window
        strategy = "TIERED_LIMITED_TIME_DISCOUNT"
    elif abandonment_minutes_elapsed <= 1440.0:
        urgency_factor = 1.0  # Max permitted salvage attempt
        strategy = "FINAL_CALL_FLASH_OFFER"
    else:
        urgency_factor = 0.7  # Diminishing return window
        strategy = "LAST_RESORT_SWEETENER"

    calculated_discount_pct = min(max_incentive_pct, round(max_incentive_pct * ltv_multiplier * urgency_factor, 1))
    absolute_savings_usd = round(cart_value_usd * (calculated_discount_pct / 100.0), 2)
    post_discount_margin_usd = round((cart_value_usd * (product_margin_pct / 100.0)) - absolute_savings_usd, 2)

    return {
        "cart_value_usd": cart_value_usd,
        "product_margin_pct": product_margin_pct,
        "customer_tier": customer_tier,
        "recovery_strategy": strategy,
        "recommended_discount_pct": calculated_discount_pct,
        "savings_offered_usd": absolute_savings_usd,
        "remaining_merchant_net_margin_usd": post_discount_margin_usd,
        "incentive_ttl_minutes": 120,
        "margin_protected": post_discount_margin_usd > 0
    }

def generate_recovery_dispatch_payload(customer_id: str, cart_id: str, approved_discount_pct: float, channel: str) -> Dict[str, Any]:
    coupon_code = f"SAVE{int(approved_discount_pct)}-{cart_id[-6:].upper()}"
    expiry_hours = 2
    
    if channel in ["sms", "whatsapp"]:
        message = f"GenPark Alert: Your reserved cart is held for {expiry_hours}h. Use code {coupon_code} for {approved_discount_pct}% off: https://checkout.genpark.ai/pay?cart={cart_id}"
    else:
        message = f"Exclusive Re-engagement: Complete your order within {expiry_hours} hours to unlock a guaranteed {approved_discount_pct}% concession with code {coupon_code}."

    return {
        "customer_id": customer_id,
        "cart_id": cart_id,
        "channel": channel,
        "coupon_code": coupon_code,
        "approved_discount_pct": approved_discount_pct,
        "expiry_window_hours": expiry_hours,
        "dispatch_message": message,
        "direct_checkout_url": f"https://checkout.genpark.ai/pay?cart={cart_id}&promo={coupon_code}",
        "status": "READY_FOR_COMMERCE_GATEWAY_DISPATCH"
    }
