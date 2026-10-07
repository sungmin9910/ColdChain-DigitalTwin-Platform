#!/bin/bash
# ================================================================
# ColdChain Jetson Split HUD Stop Script
# ================================================================

pkill -f "Step4_Jetson_SplitHUD.py" >/dev/null 2>&1
pkill -f "epiphany-browser" >/dev/null 2>&1
echo "✅ ColdChain HUD 및 브라우저가 안전하게 종료되었습니다."
