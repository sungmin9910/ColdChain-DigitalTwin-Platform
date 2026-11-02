# 3D Printer Housing — CadQuery & CQ-Editor 표준 워크플로우 가이드

`v22` 이후 모든 신규 3D 프린터 하우징 및 기구물 설계는 **CadQuery (`Python 3.10+`, `cadquery 2.7+`)** 와 **CQ-Editor**를 표준 도구로 사용합니다.

---

## 1. 폴더 구성 및 주요 파일

| 경로 | 설명 |
| :--- | :--- |
| [`v22_Apple_Sensor_Pod_Magnetic5000mAh/cadquery_v22/22_apple_sensor_pod_cq.py`](./v22_Apple_Sensor_Pod_Magnetic5000mAh/cadquery_v22/22_apple_sensor_pod_cq.py) | `v22` 사과 센서 포드 정식 CadQuery B-Rep 설계 코드 (CQ-Editor & CLI 겸용) |
| [`cadquery_template.py`](./cadquery_template.py) | 신규 버전(`v23` 등) 설계를 시작할 때 복사해서 바로 쓰는 표준 템플릿 |
| [`../AGENTS.md`](../AGENTS.md) | AI 코딩 어시스턴트가 항상 CadQuery + CQ-Editor 규격을 따르도록 강제하는 저장소 규칙 |

---

## 2. CQ-Editor에서 확인 및 편집하는 방법

1. **파일 열기**: **CQ-Editor** 실행 → 상단 메뉴 **`File` → `Open`** → 해당 버전의 `.py` 파일 선택
2. **3D 렌더링**: 단축키 **`F5`** (또는 상단 ▶ 아이콘) 클릭
3. **뷰 모드 전환**: 코드 상단 `VIEW_MODE` 값을 변경 후 **`F5`** 재실행
   * `"assembly"`: 반투명 케이스 + 내부 배터리·PCB·센서·자석 조립 검증 뷰
   * `"exploded"`: 부품 간 조립 순서를 확인하는 분해도 뷰
   * `"print_layout"`: 신도리코 3DWOX 2X 베드 바닥(`Z = 0.00 mm`) 기준 출력 정렬 뷰
4. **부품 개별 제어 & 내보내기**:
   * 우측 **`Objects`** 트리에서 원하는 부품만 체크/해제하여 내부 간섭 확인
   * 특정 부품 선택 후 **`Tools` → `Export as STEP` / `Export as STL`** 로 즉시 추출 가능

---

## 3. 터미널에서 STEP / STL 일괄 자동 생성하기

코드 수정 후 모든 부품의 `.step`(정밀 CAD 원본)과 `.stl`(슬라이서 출력용)을 한 번에 갱신하려면 터미널에서 해당 `.py` 파일을 바로 실행합니다:

```powershell
python "3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/cadquery_v22/22_apple_sensor_pod_cq.py"
```

---

## 4. 외부 STEP 부품 불러오기 팁 (실제 PCB / 센서 간섭 체크)

`3D modeling/` 폴더에 있는 실제 KiCad/EasyEDA 추출 STEP 파일을 CQ-Editor 안에서 함께 띄워 확인하려면 아래와 같이 불러올 수 있습니다:

```python
import cadquery as cq

pcb_step = cq.importers.importStep(r"..\3D modeling\3D_SensorNode_BeetleC6_50x50_2026-08-31.step")
show_object(pcb_step, name="Real_PCB_3D", options={"color": "#148c40"})
```
