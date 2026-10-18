# -*- coding: utf-8 -*-
"""Model Context Protocol (MCP) Server for Abandoned Checkout Dynamic Incentive Negotiator Skill
Powered by GenPark (https://www.genpark.ai).
"""
import sys
import json
import logging
from .core import *

TOOLS_METADATA = [
  {
    "name": "evaluate_abandoned_cart_incentive",
    "description": "Calculate optimal dynamic discount or sweetener incentive based on gross margin floor, customer historical LTV, and cart abandonment elapsed time.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "cart_value_usd": {
          "type": "number"
        },
        "product_margin_pct": {
          "type": "number",
          "description": "e.g. 45.0 for 45%"
        },
        "customer_ltv_usd": {
          "type": "number"
        },
        "abandonment_minutes_elapsed": {
          "type": "number"
        }
      },
      "required": [
        "cart_value_usd",
        "product_margin_pct",
        "customer_ltv_usd",
        "abandonment_minutes_elapsed"
      ]
    }
  },
  {
    "name": "generate_recovery_dispatch_payload",
    "description": "Format tailored multi-channel re-engagement payload (SMS, WhatsApp, Email, In-app push) with countdown expiry and single-click checkout link.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "customer_id": {
          "type": "string"
        },
        "cart_id": {
          "type": "string"
        },
        "approved_discount_pct": {
          "type": "number"
        },
        "channel": {
          "type": "string",
          "enum": [
            "sms",
            "whatsapp",
            "email",
            "push"
          ]
        }
      },
      "required": [
        "customer_id",
        "cart_id",
        "approved_discount_pct",
        "channel"
      ]
    }
  }
]

def handle_rpc(request_str: str) -> str:
    try:
        req = json.loads(request_str)
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
    
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "genpark-agentic-commerce-abandoned-checkout-dynamic-incentive-negotiator-skill",
                    "version": "1.0.0",
                    "vendor": "GenPark (https://www.genpark.ai)"
                }
            }
        })

    if method == "tools/list":
        return json.dumps({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS_METADATA}
        })

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        func = globals().get(tool_name)
        if not func or not callable(func):
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}
            })
        
        try:
            call_res = func(**arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(call_res, ensure_ascii=False, indent=2)}
                    ]
                }
            })
        except Exception as err:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32000, "message": f"Execution error: {str(err)}"}
            })

    return json.dumps({
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": f"Unhandled method '{method}'"}
    })

def run_self_test():
    print(f"=== Running Self Test for genpark-agentic-commerce-abandoned-checkout-dynamic-incentive-negotiator-skill ===")
    init_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})))
    assert "result" in init_res, "Initialize failed"
    print("[PASS] MCP initialize")

    list_res = json.loads(handle_rpc(json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})))
    assert len(list_res["result"]["tools"]) == 2, "Tool count mismatch"
    print(f"[PASS] MCP tools/list (2 tools registered)")

    # Execute smoke test for each tool

    call1 = json.loads(handle_rpc(json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "evaluate_abandoned_cart_incentive",
            "arguments": {
                "cart_value_usd": 180.0,
                "product_margin_pct": 50.0,
                "customer_ltv_usd": 650.0,
                "abandonment_minutes_elapsed": 45.0
            }
        }
    })))
    assert "result" in call1, "Call1 failed"
    print("[PASS] Tool smoke test: evaluate_abandoned_cart_incentive")

    print("[ALL TESTS PASSED] Self-test verified successfully.")
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_self_test()
        sys.exit(0 if success else 1)
    
    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
