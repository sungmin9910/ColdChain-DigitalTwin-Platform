import serial
import serial.tools.list_ports
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def find_esp_ports():
    ports = serial.tools.list_ports.comports()
    esp_ports = []
    for p in ports:
        # USB-Serial, CP210x, CH340, USB JTAG/serial debug unit 등
        esp_ports.append(p.device)
    return esp_ports

def send_and_wait(ser, command, wait_time=1.5):
    ser.reset_input_buffer()
    cmd_bytes = (command.strip() + "\n").encode('utf-8')
    ser.write(cmd_bytes)
    time.sleep(wait_time)
    lines = []
    while ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8', errors='replace').strip()
            if line:
                lines.append(line)
        except Exception:
            break
    return lines

def get_status(ser):
    lines = send_and_wait(ser, "info", wait_time=1.0)
    status_line = None
    for line in lines:
        if "LittleFS 현황" in line or "전체:" in line:
            status_line = line
            break
    return status_line, lines

def clear_storage(ser):
    lines = send_and_wait(ser, "clear", wait_time=1.2)
    clear_msg = None
    for line in lines:
        if "초기화되었습니다" in line or "LittleFS" in line:
            clear_msg = line
            break
    return clear_msg, lines

def dump_data(ser, filename="scratch/littlefs_backup.jsonl"):
    print(f"\n📡 LittleFS 블랙박스 데이터를 '{filename}' 파일로 덤프합니다...")
    ser.reset_input_buffer()
    ser.write(b"dump\n")
    
    start_time = time.time()
    last_recv_time = time.time()
    dumping = False
    count = 0
    
    with open(filename, 'w', encoding='utf-8') as f_out:
        while True:
            if time.time() - last_recv_time > 5.0 and dumping:
                break
            if time.time() - start_time > 90:
                print("⏱️ 타임아웃 도달 (90초 경과)")
                break
            
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                last_recv_time = time.time()
                
                if "LittleFS 블랙박스 덤프 시작" in line:
                    dumping = True
                    print(">>> 덤프 수신 시작...")
                    continue
                elif "덤프 종료" in line:
                    print(f">>> {line}")
                    break
                
                if dumping and line.startswith("{") and line.endswith("}"):
                    f_out.write(line + "\n")
                    count += 1
                    if count % 200 == 0:
                        print(f"   현재 {count}건 수신 중...")
            else:
                time.sleep(0.01)
                
    print(f"✅ 총 {count}건의 데이터가 '{filename}'에 안전하게 백업되었습니다.\n")

def main():
    print("=" * 60)
    print(" 🛠️ Beetle ESP32-C6 LittleFS 블랙박스 원클릭 관리 도구")
    print("=" * 60)
    
    available_ports = find_esp_ports()
    if not available_ports:
        print("❌ 연결된 시리얼(COM) 포트를 찾을 수 없습니다. USB 케이블 연결을 확인하세요.")
        return

    # 기본 포트 자동 선택 (COM17이 목록에 있으면 우선 선택)
    default_port = "COM17" if "COM17" in available_ports else available_ports[0]
    print(f"감지된 COM 포트: {', '.join(available_ports)}")
    selected_port = input(f"연결할 포트를 입력하세요 [기본값: {default_port}]: ").strip()
    if not selected_port:
        selected_port = default_port

    baud = 115200
    try:
        ser = serial.Serial(selected_port, baud, timeout=2)
        ser.dtr = True
        ser.rts = True
        time.sleep(1.0)
    except Exception as e:
        print(f"❌ {selected_port} 포트를 열 수 없습니다: {e}")
        return

    print(f"\n🔌 {selected_port} 연결 성공! (Baud: {baud})")

    while True:
        print("\n" + "-" * 50)
        print(" [메뉴를 선택하세요]")
        print(" 1. 📊 LittleFS 저장 현황 및 용량 확인 (Check)")
        print(" 2. 🗑️ LittleFS 완전 비우기 / 0건 초기화 (Clear)")
        print(" 3. 💾 LittleFS 데이터 PC 백업 덤프 받기 (Backup)")
        print(" 4. 🚪 종료 (Exit)")
        print("-" * 50)
        
        choice = input("👉 선택 (1/2/3/4): ").strip()
        
        if choice == "1":
            print("\n🔍 ESP32-C6에 상태 조회를 요청합니다...")
            stat, all_lines = get_status(ser)
            if stat:
                print(f"✅ {stat}")
            else:
                print("📋 수신된 응답:")
                for l in all_lines:
                    print(f"   {l}")
                    
        elif choice == "2":
            confirm = input("⚠️ 정말로 LittleFS의 모든 로그를 삭제하고 0건으로 비우시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                msg, _ = clear_storage(ser)
                if msg:
                    print(f"✅ {msg}")
                else:
                    print("✅ [LittleFS] 삭제 및 초기화 명령이 전송되었습니다.")
                # 비운 후 상태 재확인
                time.sleep(0.5)
                stat, _ = get_status(ser)
                if stat:
                    print(f"👉 초기화 후 상태: {stat}")
            else:
                print("취소되었습니다.")
                
        elif choice == "3":
            dump_data(ser)
            
        elif choice == "4":
            print("프로그램을 종료합니다.")
            break
        else:
            print("올바른 번호를 입력하세요.")

    ser.close()

if __name__ == "__main__":
    main()
