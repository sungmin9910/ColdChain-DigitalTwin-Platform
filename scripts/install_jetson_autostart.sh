#!/bin/bash
# ================================================================
# ColdChain Jetson 자동 실행 및 바탕화면 바로가기 등록 스크립트
# ================================================================

export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 1. 쉘 스크립트 실행 권한 부여
chmod +x "$SCRIPT_DIR/run_jetson_hud.sh"
chmod +x "$SCRIPT_DIR/stop_jetson_hud.sh"

# 2. 바탕화면 폴더 감지 (영문/한글 환경 및 xdg-user-dir 모두 등록)
DESKTOP_DIRS=()
XDG_DESK="$(xdg-user-dir DESKTOP 2>/dev/null)"
[ -n "$XDG_DESK" ] && DESKTOP_DIRS+=("$XDG_DESK")
[ -d "$HOME/Desktop" ] && DESKTOP_DIRS+=("$HOME/Desktop")
[ -d "$HOME/바탕화면" ] && DESKTOP_DIRS+=("$HOME/바탕화면")

# 중복 제거
UNIQUE_DESK_DIRS=($(printf "%s\n" "${DESKTOP_DIRS[@]}" | sort -u))

for DDIR in "${UNIQUE_DESK_DIRS[@]}"; do
    mkdir -p "$DDIR"
    
    # [실행 아이콘]
    RUN_ICON="$DDIR/ColdChain_HUD_실행.desktop"
    cat <<EOF > "$RUN_ICON"
[Desktop Entry]
Version=1.0
Type=Application
Name=ColdChain HUD 실행
Comment=Start ColdChain Jetson Split HUD Dashboard
Exec=$SCRIPT_DIR/run_jetson_hud.sh
Icon=utilities-system-monitor
Terminal=false
Categories=Utility;Development;
StartupNotify=true
EOF
    chmod +x "$RUN_ICON"
    gio set "$RUN_ICON" metadata::trusted true >/dev/null 2>&1

    # [종료 아이콘]
    STOP_ICON="$DDIR/ColdChain_HUD_종료.desktop"
    cat <<EOF > "$STOP_ICON"
[Desktop Entry]
Version=1.0
Type=Application
Name=ColdChain HUD 종료
Comment=Stop ColdChain Jetson Split HUD Dashboard
Exec=$SCRIPT_DIR/stop_jetson_hud.sh
Icon=process-stop
Terminal=false
Categories=Utility;Development;
StartupNotify=false
EOF
    chmod +x "$STOP_ICON"
    gio set "$STOP_ICON" metadata::trusted true >/dev/null 2>&1
done

# 3. 우분투 애플리케이션 메뉴(Super/Win 키 검색 목록)에도 등록
APP_MENU_DIR="$HOME/.local/share/applications"
mkdir -p "$APP_MENU_DIR"
cat <<EOF > "$APP_MENU_DIR/ColdChain_HUD.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=ColdChain HUD (콜드체인 관제)
Comment=ColdChain Jetson Split HUD
Exec=$SCRIPT_DIR/run_jetson_hud.sh
Icon=utilities-system-monitor
Terminal=false
Categories=Utility;
EOF
chmod +x "$APP_MENU_DIR/ColdChain_HUD.desktop"

# 4. 부팅 시 자동 시작(Autostart) 등록
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cat <<EOF > "$AUTOSTART_DIR/ColdChain_HUD.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=ColdChain HUD Autostart
Comment=Auto-launch ColdChain Jetson Split HUD on Login
Exec=/bin/bash -c "sleep 4 && $SCRIPT_DIR/run_jetson_hud.sh"
Icon=utilities-system-monitor
Terminal=false
Categories=Utility;
X-GNOME-Autostart-enabled=true
EOF
chmod +x "$AUTOSTART_DIR/ColdChain_HUD.desktop"

echo "============================================================"
echo "🎉 젯슨 자동 실행 설정이 완료되었습니다!"
echo "============================================================"
echo "1. 🖥️ 바탕화면 아이콘: [ColdChain HUD 실행] 등록 완료"
echo "2. 🚀 부팅 시 자동 실행: ~/.config/autostart 등록 완료"
echo ""
echo "🚀 [지금 즉시 대시보드 화면을 엽니다...]"
echo "============================================================"

# 설치 즉시 화면 띄우기
bash "$SCRIPT_DIR/run_jetson_hud.sh"
echo "✅ 대시보드 및 브라우저가 화면에 열렸습니다!"
