import os
import subprocess
import sys

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    while True:
        print("\n" + "="*50)
        print(" [ QR 스캐너 실행 메뉴 (A10 ~ A14) ]")
        print(" 1. scan1.py (A10 - 입고)")
        print(" 2. scan2.py (A11 - 세척)")
        print(" 3. scan3.py (A12 - 선별)")
        print(" 4. scan4.py (A13 - 포장)")
        print(" 5. scan5.py (A14 - 출고)")
        print(" 0. 종료")
        print("="*50)
        
        choice = input("실행할 단계의 번호를 입력하세요 (0~5): ").strip()
        
        if choice == '0':
            print("프로그램을 종료합니다.")
            break
        elif choice in ['1', '2', '3', '4', '5']:
            script_name = f"scan{choice}.py"
            script_path = os.path.join(base_dir, script_name)
            
            if os.path.exists(script_path):
                print(f"\n>>> [{script_name}] 실행 중... (종료하려면 Ctrl+C를 누르세요)")
                try:
                    # 선택한 파이썬 스크립트 실행
                    subprocess.run([sys.executable, script_path])
                except KeyboardInterrupt:
                    print(f"\n[INFO] {script_name} 실행이 중단되었습니다. 메뉴로 돌아갑니다.")
                except Exception as e:
                    print(f"\n[ERROR] 스크립트 실행 중 오류 발생: {e}")
            else:
                print(f"\n[ERROR] {script_name} 파일을 찾을 수 없습니다: {script_path}")
        else:
            print("\n[WARNING] 잘못된 입력입니다. 0부터 5 사이의 숫자를 입력해주세요.")

if __name__ == "__main__":
    main()
