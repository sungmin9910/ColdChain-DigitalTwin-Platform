# ColdChain-DigitalTwin-Platform 에이전트 작업 규칙 (AGENTS.md)

## 3D 모델링 및 기구 설계 표준 (CadQuery + CQ-Editor 필수)

이 저장소(`3D_Printer_Housing/`, `3D modeling/` 및 모든 신규 하우징·브래킷·지그 설계)에서 앞으로 진행하는 모든 3D 모델링 작업은 기존 OpenSCAD(`.scad`) 대신 **CadQuery (`cadquery 2.7+`, Python B-Rep)** 와 **CQ-Editor** 기준으로 작성하고 관리한다.

### 1. 필수 구현 규칙 (Dual-Mode 스크립트 구조)
모든 신규 3D 모델링 파이썬 스크립트(`.py`)는 **CQ-Editor GUI(`F5` 렌더링)** 와 **터미널 일괄 빌드(`python script.py`)** 두 가지 환경에서 모두 즉시 동작해야 한다:

1. **CQ-Editor 호환 (`show_object` + `VIEW_MODE`)**:
   - 스크립트 상단에 `VIEW_MODE = "assembly"` (예: `"assembly"`, `"exploded"`, `"print_layout"`, 개별 단품명) 변수를 배치해 CQ-Editor에서 문자열만 바꾸고 `F5`를 눌러 뷰를 전환할 수 있게 한다.
   - 스크립트 하단에서 `if "show_object" in globals():` 조건으로 CQ-Editor 실행 환경을 자동 감지하고, `show_object(part, name="부품명", options={"color": "#HEX코드", "alpha": 투명도})` 형태로 등록해 CQ-Editor의 `Objects` 트리에서 부품별 켜기/끄기가 가능하도록 한다.
   - 색상은 모든 버전의 CQ-Editor(`pyqtgraph`) 호환을 위해 반드시 `0~255` 정수 튜플 또는 `"#RRGGBB"` HEX 문자열을 사용한다.
2. **터미널 일괄 출력 (`elif __name__ == "__main__":`)**:
   - 정밀 CAD 원본인 **`.step`** (단품 및 `cq.Assembly` 조립체) 파일과 3D 프린터 슬라이서용 **`.stl`** (`tolerance=0.04, angularTolerance=0.08`) 파일을 동시에 내보낸다.
   - 신도리코 **3DWOX 2X** 출력용 `.stl` 부품은 별도 수동 회전 없이 바로 슬라이싱할 수 있도록 출력 방향 정렬 및 베드 바닥 밀착(`Z_min = 0.00 mm`) 상태로 저장한다.

### 2. B-Rep 모델링 및 사전 검증 주의사항
- **`Workplane("XZ")` 법선 방향 유의**: `cq.Workplane("XZ")`의 로컬 `(x, y)`는 글로벌 `(+X, +Z)`이며 기본 돌출 법선(`zDir`)은 글로벌 **`-Y`** 방향이다. `+Y` 방향 돌출 시 새 평면을 임의 생성해 `Z`축 부호가 뒤집히지 않도록 `Workplane("XZ")`에서 음수 오프셋/음수 돌출(`extrude(-길이)`)을 활용하거나 로컬 축 방향을 사전 검증한다.
- **공면(Coplanar) 불리언 아티팩트 방지**: 반구 분할 시 먼저 전체 중공 바디(`hollow = outer.cut(inner)`)를 생성한 뒤 분할 박스와 `.intersect()`하여 경계면 얇은 막(Sliver) 발생을 원천 차단한다.
- **실제 STEP 부품 활용**: `3D modeling/` 폴더 내 실제 PCB 및 센서 STEP 파일(`3D_SensorNode_BeetleC6_50x50_2026-08-31.step` 등)이 필요한 경우 `cq.importers.importStep()`으로 불러와 정밀 간섭 검사를 수행할 수 있다.
- **사전 검증 필수**: 모델 생성 후 `tessellate()` 정밀 치수 확인 및 `vtk` 오프스크린 렌더링 이미지 검수를 거쳐 형상 오류나 축 반전이 없는지 확인한 뒤 GitHub에 커밋·푸시한다.

### 3. 기준 레퍼런스 및 템플릿 경로
- **실전 변환 레퍼런스**: `3D_Printer_Housing/v22_Apple_Sensor_Pod_Magnetic5000mAh/cadquery_v22/22_apple_sensor_pod_cq.py`
- **신규 버전 시작 템플릿**: `3D_Printer_Housing/cadquery_template.py`
- **워크플로우 안내서**: `3D_Printer_Housing/README.md`
