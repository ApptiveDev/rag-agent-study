## 1. 포트 점유 충돌: "왜 내 서비스가 8000번 포트를 못 쓰지?"

### **문제 상황**

신규 FastAPI 서비스를 실행하려는데 `Address already in use` 에러가 발생하며 8000번 포트를 사용하지 못함.

### **원인**

과거에 `/srv/insole-server/` 경로에서 실행했던 옛날 서비스 프로세스가 시스템 서비스(systemd)로 등록되어 이미 8000번 포트를 점유하고 있었음.

### **해결 과정**

1. `ps -ef | grep 8000`으로 범인 프로세스 PID 확인.
2. `grep -r`을 이용해 `/etc/systemd/system/`에서 해당 프로세스를 실행 중인 서비스 파일명 탐색.
3. `/srv` 경로를 바라보던 유령 서비스를 중단.

### **최종 해결**

Bash

`sudo systemctl stop [옛날서비스명]
sudo systemctl disable [옛날서비스명]
sudo systemctl restart insole-api  # 진짜 서비스 실행`

---

## 2. Nginx 405 Method Not Allowed: "POST 요청이 왜 안 돼?"

### **문제 상황**

로그인 버튼을 눌렀는데 `405 Not Allowed` 에러 발생.

### **원인**

Nginx가 `/api/` 요청을 백엔드(FastAPI)로 넘겨주지 않고, 자신의 정적 파일 폴더에서 `/api`라는 파일을 찾으려 함. Nginx는 기본적으로 정적 파일에 대한 `POST` 요청을 허용하지 않음.

### **해결 과정**

Vite의 `proxy` 설정은 로컬 개발용일 뿐, 배포 환경에서는 Nginx가 그 역할을 대신해야 함을 인지.

### **최종 해결**

Nginx 설정 파일(`sites-available`)에 `location /api/` 블록을 추가하고 `proxy_pass`로 8000번 포트 연결.

---

## 3. Nginx 500/403 Permission Denied: "파일은 있는데 왜 못 읽니?"

### **문제 상황**

웹사이트 접속 시 흰 화면이 뜨거나 이미지(assets) 로딩 시 `500 Internal Server Error` 또는 `403 Forbidden` 발생.

### **원인**

Nginx 실행 계정(`www-data`)이 사용자의 홈 디렉토리(`/home/ubuntu`) 내부에 있는 빌드 파일에 접근할 권한이 없었음. 권한이 막히자 Nginx가 `try_files` 설정에 의해 무한 루프에 빠짐.

### **해결 과정**

1. Nginx 에러 로그(`/var/log/nginx/error.log`)에서 `Permission denied` 확인.
2. 상위 폴더인 `/home/ubuntu`부터 실행 권한(`+x`)이 있는지 체크.

### **최종 해결**

상위 폴더부터 하위 빌드 파일까지 Nginx가 접근할 수 있도록 권한 부여.

Bash

`sudo chmod 755 /home/ubuntu
sudo chmod -R 755 /var/www/manage/dist`

---

## 4. 경로 미스터리: "내가 알던 dist가 그 dist가 아니다"

### **문제 상황**

Nginx 설정을 마쳤는데도 계속 404가 뜨거나, 뜬금없이 AWS CLI 관련 파일들만 보임.

### **원인**

서버 내에 `dist`라는 이름의 폴더가 여러 개 존재함. 특히 `/home/ubuntu/aws/dist`는 AWS CLI 설치 파일이었는데, Nginx가 이곳을 웹사이트 루트로 바라보고 있었음.

### **해결 과정**

1. `find / -name "index.html"` 명령어로 서버 전체에서 진짜 관리자 페이지 빌드물이 어디 있는지 수색.
2. `/var/www/manage/dist`라는 진짜 경로를 찾아냄.

### **최종 해결**

Nginx 설정 파일의 `root` 경로를 가짜 폴더(`~/aws/dist`)에서 진짜 폴더(`/var/www/manage/dist`)로 전격 수정.

---

### **💡 블로그 포스팅**

- **제목 추천:** "EC2에서 React + FastAPI 배포하며 겪은 Nginx 삽질기 (403, 404, 405, 500 완벽 정리)"
- **핵심 교훈:** "Nginx 설정을 바꿨다면 반드시 에러 로그(`tail -f /var/log/nginx/error.log`)를 먼저 확인하자!"
- **마무리:** 백엔드는 `git push` 자동 배포, 프론트는 `scp` 수동 배포로 이원화하여 관리하는 효율적인 워크플로우 소개.