# Morai ZED LANDMARK Demo — 설치 및 실행 가이드

본 가이드는 ZED 카메라 또는 SVO 파일을 활용한 Morai Landmark Demo를 실행할 수 있도록 작성되었습니다.

<br />

## 0. 폴더 구성

```
morai-zed-landmark/
│
├── demo.py              # 메인 데모 코드
├── setup_env.bat        # 환경 설정 스크립트
├── run.bat              # 실행 스크립트
└── requirements.txt     # 필요한 Python 라이브러리 목록
```

---

## 1. 설치 준비

### 필수 프로그램
- **Python 3.12 (64bit)**  
  🔗 [https://www.python.org/downloads/](https://www.python.org/downloads/)  
  설치 시 반드시 **“Add Python to PATH”** 옵션을 체크하세요 ✅

- **ZED SDK 4.x 이상**  
  🔗 [https://www.stereolabs.com/developers/](https://www.stereolabs.com/developers/)  
  설치 후 아래 경로 중 하나에 존재해야 합니다:
    ```
    C:\Program Files\ZED SDK
    C:\Program Files (x86)\ZED SDK
    ```
  
---

## 2. 환경 세팅 (최초 1회만 실행)

1. setup_env.bat 더블클릭 실행

   자동으로 아래 작업이 수행됩니다.
   ① Python 가상환경 생성
   ② 필요한 패키지(pip install) 설치
   ③ ZED SDK 경로 자동 탐색 및 Python API 설치
   ④ 설치 확인(pyzed.sl import 테스트)

2. 완료 후 콘솔에 아래 메시지가 보이면 성공입니다:
   [DONE] Environment setup complete!
   ZED Python API version: 4.x.x

⚠️ 설치가 중간에 꺼진다면
   setup_env.bat을 관리자 권한으로 다시 실행해주세요.

3. 배치파일 동작이 어려운 경우 명령어 리스트
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

venv/Scripts/activate

python -m pip install --upgrade pip
 
pip install -r requirements.txt

python C:\"Program Files (x86)"\"ZED SDK"\get_python_api.py
```

---

## 3. 데모 실행 (ZED 카메라 / SVO 파일)

```
1. ZED 카메라를 PC에 연결합니다.
2. run.bat을 더블클릭합니다.
3. ZED 카메라가 실시간으로 표시됩니다.
   종료하려면 ESC 또는 Q 키를 누르세요.
```

---

## 4. 참고 명령어 (선택적)

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate 
python demo.py --mode zed
python demo.py --mode svo --svo data/sample.svo
```

---

## 5. 터미널용

### 1) 셋업
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
py -3.12 -m venv venv
venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python C:\"Program Files (x86)"\"ZED SDK"\get_python_api.py
```

### 2) 실행
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate 
python demo.py --mode zed
```
