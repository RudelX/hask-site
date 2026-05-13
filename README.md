# 해스크 내전봇 배포 가이드

## 필요한 환경변수 (Railway에서 설정)

| 변수명 | 설명 |
|--------|------|
| BOT_TOKEN | Discord Bot 토큰 |
| GUILD_ID | Discord 서버 ID (1272943446998388887) |
| FIREBASE_CRED | Firebase 서비스 계정 JSON (통째로 붙여넣기) |

## Railway 배포 순서

1. https://railway.app 접속 → GitHub 로그인
2. New Project → Deploy from GitHub repo
3. 이 폴더를 GitHub에 업로드 후 연결
4. Variables 탭에서 환경변수 3개 설정
5. Deploy 클릭

## Firebase 서비스 계정 키 발급 방법

1. Firebase 콘솔 → 프로젝트 설정
2. 서비스 계정 탭
3. "새 비공개 키 생성" 클릭
4. 다운로드된 JSON 파일 내용 전체를
   FIREBASE_CRED 환경변수에 붙여넣기
