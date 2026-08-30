# 50mm x 50mm 스마트 농업 센서 노드 (Beetle ESP32-C6) PCB 프로젝트

본 프로젝트는 `11_50x50_스마트농업_센서노드_PCB_설계_및_EasyEDA_가이드.pdf` 문서의 물리 사양, 부품 배치 정밀 좌표, 핀 매핑(Netlist)을 100% 반영하여 생성된 프로젝트입니다.

---

## 📁 생성된 파일 목록

| 파일명 | 설명 | 용도 |
| :--- | :--- | :--- |
| **`SensorNode_BeetleC6_50x50.kicad_pcb`** | 50×50mm 정밀 PCB 레이아웃 파일 | EasyEDA 가져오기 및 KiCad 열기용 |
| **`SensorNode_BeetleC6_50x50.kicad_sch`** | 회로도 (Schematic) 파일 | EasyEDA 가져오기 및 회로 검증용 |
| **`SensorNode_BeetleC6_50x50.kicad_pro`** | KiCad 프로젝트 설정 파일 | KiCad 7 / 8 / 10 프로젝트 연동 |
| **`SensorNode_BeetleC6_50x50_EasyEDA_Source.json`** | EasyEDA 전용 JSON 소스 파일 | EasyEDA Source 직접 열기용 |

---

## 🌐 EasyEDA에서 여는 방법 (10초 소요)

### 방법 1: EasyEDA 웹 에디터에서 KiCad 파일 가져오기 (가장 추천 🌟)
1. 웹 브라우저로 **[EasyEDA Editor](https://easyeda.com/editor)** 에 접속합니다. (로그인)
2. 상단 메뉴에서 **`File (파일)`** ➔ **`Import (가져오기)`** ➔ **`KiCad`** 를 클릭합니다.
3. 파일 선택 창에서 다음 파일 중 하나를 선택합니다:
   - **`SensorNode_BeetleC6_50x50.kicad_pcb`** (PCB 레이아웃 즉시 로드)
   - **`SensorNode_BeetleC6_50x50.kicad_sch`** (회로도 즉시 로드)
4. 화면에 **50mm × 50mm 기판, M3 나사홀 4개, Beetle ESP32-C6, 센서 풋프린트, 배선**이 자동으로 완벽하게 로드됩니다!

### 방법 2: EasyEDA Source JSON으로 열기
1. EasyEDA Editor 상단 메뉴 **`File (파일)`** ➔ **`Open (열기)`** ➔ **`EasyEDA Source`** 선택
2. **`SensorNode_BeetleC6_50x50_EasyEDA_Source.json`** 파일 선택

---

## 🔍 3D 뷰어 확인 및 STEP 3D 파일 내보내기

1. EasyEDA 상단 메뉴에서 **`View (보기)`** ➔ **`3D View (3D 보기)`** 를 클릭합니다.
2. 실시간으로 렌더링된 50×50mm 3D 기판을 확인합니다.
3. 3D 캐드(Fusion 360, SolidWorks, Onshape 등)로 가져가려면:
   - 상단 메뉴 **`File`** ➔ **`Export`** ➔ **`3D Model (*.STEP)`** 클릭하여 다운로드

---

## 🏭 JLCPCB 발주용 Gerber 파일 추출 방법

1. EasyEDA 상단 메뉴에서 **`Fabrication (제작)`** ➔ **`PCB Fabrication File (Gerber)`** 클릭
2. 생성된 ZIP 파일을 다운로드하여 JLCPCB 또는 국내 PCB 제조사에 업로드하면 즉시 견적 및 제작 진행 가능합니다.
