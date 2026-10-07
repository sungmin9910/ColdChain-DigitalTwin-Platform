#!/bin/bash
# ================================================================
# ColdChain Jetson 자동 실행 및 바탕화면 아이콘 해제 스크립트
# ================================================================

rm -f "$HOME/Desktop/ColdChain_HUD_실행.desktop"
rm -f "$HOME/Desktop/ColdChain_HUD_종료.desktop"
rm -f "$HOME/바탕화면/ColdChain_HUD_실행.desktop"
rm -f "$HOME/바탕화면/ColdChain_HUD_종료.desktop"
rm -f "$HOME/.local/share/applications/ColdChain_HUD.desktop"
rm -f "$HOME/.config/autostart/ColdChain_HUD.desktop"

echo "✅ 젯슨 자동 실행 및 바탕화면 아이콘이 모두 삭제되었습니다."
