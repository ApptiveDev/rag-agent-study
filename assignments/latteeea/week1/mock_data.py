"""Mock troubleshooting notes for the week1 Engineering Narrative Agent."""

TROUBLESHOOTING_NOTES = [
    {
        "id": "long-polling-db-pool-exhaustion",
        "title": "Long Polling 구현으로 인한 DB Connection Pool 고갈",
        "category": "backend_scalability",
        "tech_stack": ["FastAPI", "SQLAlchemy", "PostgreSQL", "Long Polling"],
        "symptom": "키오스크 기기 추가 후 서버가 몇 분 만에 강제 종료",
        "impact": "매장 기기와 관리자 기능 전체 이용 불가",
        "timeline": [
            "기기 1대 추가",
            "서버 다운 발생",
            "DB 점유율 증가 확인",
            "pool_size/overflow 임시 증가",
            "system-status 로그 폭주 확인",
            "since 파라미터 누락 발견",
            "long polling 구조와 DB session 생명주기 재검토",
        ],
        "investigation_steps": [
            {
                "step": 1,
                "hypothesis": "단순히 DB connection 수가 부족하다",
                "action": "pool_size와 overflow 증가",
                "observation": "일시적으로 버티지만 근본 해결은 아님",
                "result": "partial",
            },
            {
                "step": 2,
                "hypothesis": "long polling 요청이 DB session을 오래 물고 있다",
                "action": "SQLAlchemy session 생명주기와 long polling loop 확인",
                "observation": "요청이 살아있는 동안 connection이 pool로 반환되지 않음",
                "result": "confirmed",
            },
            {
                "step": 3,
                "hypothesis": "클라이언트가 즉시 재요청하면서 로그가 폭주한다",
                "action": "since 파라미터 확인",
                "observation": "since가 None으로 들어와 즉시 전체 반환 분기 실행",
                "result": "confirmed",
            },
        ],
        "root_cause": "long polling loop 내부에서 SQLAlchemy Session이 트랜잭션/커넥션을 오래 점유했고, 클라이언트 수 증가에 따라 connection pool이 고갈됨",
        "solution": "check_interval 조정, pool_size/overflow 임시 증가, since 파라미터 처리, 장기적으로는 session 반환 구조 개선 또는 SSE 검토",
        "structural_insight": "이 문제는 결국 서버 성능 문제가 아니라 긴 요청과 DB connection 생명주기를 분리하지 못한 구조 문제였다.",
        "content_angle": "데이터 변경이 드문 기능이라 long polling이 효율적일 거라 생각했지만, 서버 리소스 관점에서는 오히려 위험할 수 있었던 사례",
        "blog_value": 5,
        "evidence": [
            "키오스크 기기 추가 후 서버가 몇 분 안에 강제 종료됨",
            "DB 점유율 증가 및 QueuePool timeout 발생",
            "long polling 요청이 SQLAlchemy session을 장시간 유지",
            "session이 commit/rollback/close 되기 전까지 connection pool로 반환되지 않음",
            "동시 polling 요청 수 증가 시 session과 connection이 함께 장시간 점유됨",
            "pool_size 및 max_overflow 증가 시 일시적으로 완화되었지만 근본 해결은 되지 않음",
            "system-status 로그가 비정상적으로 빠르게 반복 출력됨",
            "since 파라미터가 None으로 들어가며 즉시 전체 반환 분기가 반복 실행됨",
            "check_interval을 1초 → 3초로 변경 후 로그 빈도 감소",
            "클라이언트 수 증가에 따라 열린 long polling 요청 수가 선형적으로 증가",
            "일반 polling 대비 long polling이 항상 더 효율적인 것은 아님을 확인",
            "DB polling 기반 long polling 구현은 polling과 유사한 DB 부하를 유발",
            "SSE가 점검 상태 같은 단방향 push 구조에 더 적합할 수 있다는 점 검토",
            "근본 해결을 위해 long polling loop 내부에서 매 반복마다 session 종료 및 connection 반환 필요"
        ],
    },
    {
        "id": "android-cleartext-network-security-config",
        "title": "Android HTTP 서버 연결 실패와 Network Security Config 설정",
        "category": "mobile_networking",
        "tech_stack": ["React-Native", "Expo", "EAS Build", "Android", "iOS", "HTTP"],
        "project": "mobile-app",
        "severity": "medium",

        "symptom": (
            "개발 서버가 HTTPS가 아닌 HTTP로 운영되는 상황에서, iOS에서는 서버 연결이 되지만 "
            "Android APK 설치 후 서버에 연결할 수 없다는 에러가 발생했다."
        ),
        "impact": (
            "React Native Expo 앱을 Android/iOS 동시 빌드하는 과정에서 Android 실기기 테스트 및 "
            "APK 배포 검증이 막혔다."
        ),

        "timeline": [
            "개발 서버에 SSL을 붙이지 못해 HTTP endpoint를 사용했다.",
            "React Native Expo 및 EAS Build로 Android/iOS 동시 빌드를 진행했다.",
            "iOS에서는 서버 연결이 정상 동작했다.",
            "Android APK 설치 후 서버에 연결할 수 없다는 에러가 발생했다.",
            "Android 9 이상에서 cleartext HTTP traffic이 기본 차단된다는 점을 확인했다.",
            "app.json에 usesCleartextTraffic 설정을 추가했다.",
            "network_security_config.xml을 생성하고 AndroidManifest application 태그에 연결했다.",
            "prebuild 시 AndroidManifest 설정이 덮어씌워질 수 있어 Expo config plugin으로 자동 주입하도록 구성했다."
        ],

        "investigation_steps": [
            {
                "step": 1,
                "hypothesis": "서버 URL 또는 로컬 IP 주소 설정이 잘못되었을 것이다.",
                "action": "실기기에서 접근 가능한 HTTP 서버 주소와 IP를 확인했다.",
                "observation": "iOS에서는 같은 서버로 연결이 되었고, Android에서만 실패했다.",
                "result": "rejected"
            },
            {
                "step": 2,
                "hypothesis": "Android 플랫폼의 HTTP cleartext traffic 차단 정책 때문일 것이다.",
                "action": "Android 9+의 cleartext HTTP 차단 정책과 Expo Android 설정을 확인했다.",
                "observation": "Android에서는 HTTP 통신을 허용하려면 usesCleartextTraffic 또는 network security config 설정이 필요했다.",
                "result": "confirmed"
            },
            {
                "step": 3,
                "hypothesis": "app.json 설정만으로 Android 네이티브 설정이 안정적으로 유지될 것이다.",
                "action": "app.json에 android.usesCleartextTraffic=true를 추가했다.",
                "observation": "prebuild 과정에서 AndroidManifest나 native config가 다시 생성되며 수동 설정이 사라질 수 있었다.",
                "result": "partial"
            },
            {
                "step": 4,
                "hypothesis": "Expo config plugin으로 native config를 빌드 시점마다 주입해야 한다.",
                "action": "withAndroidManifest와 withDangerousMod를 사용해 network_security_config.xml 생성 및 Manifest 속성 주입 plugin을 작성했다.",
                "observation": "prebuild 이후에도 필요한 Android HTTP 허용 설정을 유지할 수 있는 구조가 되었다.",
                "result": "confirmed"
            }
        ],

        "root_cause": (
            "Android 9 이상에서는 cleartext HTTP traffic이 기본적으로 차단되는데, "
            "Android native network security config와 Manifest 설정이 안정적으로 주입되지 않아 HTTP 서버 연결이 실패했다."
        ),
        "solution": (
            "app.json의 usesCleartextTraffic 설정과 함께 network_security_config.xml을 생성하고, "
            "AndroidManifest application 태그에 android:usesCleartextTraffic 및 android:networkSecurityConfig를 연결했다. "
            "prebuild 시 설정이 덮어씌워지는 문제를 막기 위해 Expo config plugin으로 자동 주입했다."
        ),
        "structural_insight": (
            "이 문제는 결국 서버 연결 문제가 아니라 플랫폼별 네트워크 보안 정책과 Expo prebuild 구조를 이해하지 못한 문제였다."
        ),
        "content_angle": (
            "iOS에서는 되는데 Android에서만 HTTP 서버 연결이 실패할 때, 네트워크 문제가 아니라 플랫폼 보안 정책과 native config 생성 흐름을 봐야 한다는 사례"
        ),
        "blog_value": 4,
        "evidence": [
            "iOS에서는 동일 HTTP 서버 연결 성공",
            "Android APK에서 서버 연결 실패",
            "Android 9+ cleartext HTTP 기본 차단",
            "usesCleartextTraffic 및 network_security_config.xml 필요",
            "prebuild 시 native 설정이 덮어씌워질 수 있음"
        ],
        "related_notes": [
            "x-username-auth-boundary",
            "onedrive-eas-android-build-permission"
        ]
    },

    {
        "id": "react-usecallback-context-infinite-render",
        "title": "React useCallback dependency에 Context 객체를 넣어 발생한 무한 렌더링",
        "category": "frontend_state_management",
        "tech_stack": ["React", "TypeScript", "Context API", "useCallback", "useRef"],
        "project": "admin-web",
        "severity": "medium",

        "symptom": (
            "게시물 작성/수정 페이지 진입 직후 Maximum update depth exceeded 에러가 발생했고, "
            "렌더링 횟수와 콘솔 에러가 무한히 증가했다."
        ),
        "impact": (
            "페이지 진입만 해도 state update와 render가 반복되어 정상적인 게시물 작성/수정 기능을 사용할 수 없었다."
        ),

        "timeline": [
            "Cursor로 게시물 작성/수정 페이지를 구현했다.",
            "페이지 진입 직후 콘솔에 Maximum update depth exceeded 에러가 발생했다.",
            "state 업데이트와 렌더링이 반복되는 구조임을 확인했다.",
            "handlePublish가 useCallback으로 감싸져 있고 dependency array에 healthEdit Context 객체가 들어가 있음을 확인했다.",
            "handlePublish 내부에서 healthEdit.setPublishLoading이 호출되며 Context 상태가 변경되었다.",
            "Context 객체 변경으로 handlePublish가 재생성되고, 다시 상태 변경을 유발하는 순환 구조를 파악했다.",
            "healthEdit 객체를 dependency에서 제거하고 필요한 setter만 useRef로 참조하도록 수정했다."
        ],

        "investigation_steps": [
            {
                "step": 1,
                "hypothesis": "API 호출이나 게시물 데이터 초기화 로직이 반복 실행되고 있을 것이다.",
                "action": "페이지 진입 시점의 콘솔 에러와 렌더링 증가 패턴을 확인했다.",
                "observation": "네트워크 문제가 아니라 setState와 render가 반복되는 React 상태 업데이트 문제였다.",
                "result": "rejected"
            },
            {
                "step": 2,
                "hypothesis": "useEffect dependency array 문제일 것이다.",
                "action": "상태 업데이트가 발생하는 effect와 callback dependency를 확인했다.",
                "observation": "직접적인 useEffect 문제라기보다 useCallback dependency에 매 렌더마다 바뀔 수 있는 Context 객체가 포함되어 있었다.",
                "result": "partial"
            },
            {
                "step": 3,
                "hypothesis": "healthEdit Context 객체가 handlePublish 재생성을 유발하고 있을 것이다.",
                "action": "handlePublish dependency array와 내부의 healthEdit.setPublishLoading 호출 흐름을 추적했다.",
                "observation": "handlePublish 실행 → Context 상태 변경 → healthEdit 객체 변경 → handlePublish 재생성으로 이어지는 순환 가능성이 있었다.",
                "result": "confirmed"
            },
            {
                "step": 4,
                "hypothesis": "콜백은 안정적으로 유지하고 최신 setter만 ref로 읽으면 순환을 끊을 수 있다.",
                "action": "setPublishLoadingRef를 만들고 healthEdit를 dependency array에서 제거했다.",
                "observation": "ref.current만 갱신되고 handlePublish 참조는 안정적으로 유지되어 무한 렌더링이 해결되었다.",
                "result": "confirmed"
            }
        ],

        "root_cause": (
            "useCallback dependency array에 렌더마다 바뀔 수 있는 healthEdit Context 객체를 넣었고, "
            "callback 내부에서 해당 Context 상태를 변경하면서 callback 재생성과 상태 변경이 순환했다."
        ),
        "solution": (
            "healthEdit 객체를 useCallback dependency에서 제거하고, 필요한 setPublishLoading 함수는 useRef에 저장해 "
            "Stable Callback + Ref Pattern으로 참조했다."
        ),
        "structural_insight": (
            "이 문제는 결국 단순한 useEffect 에러가 아니라 렌더링 생명주기와 함수 참조 안정성을 분리하지 못한 상태 설계 문제였다."
        ),
        "content_angle": (
            "React의 Maximum update depth exceeded 에러를 단순 dependency 누락이 아니라 Context 객체 참조 안정성과 callback 설계 관점에서 분석한 사례"
        ),
        "blog_value": 4,
        "evidence": [
            "Maximum update depth exceeded 에러",
            "handlePublish useCallback dependency에 healthEdit 포함",
            "handlePublish 내부에서 healthEdit.setPublishLoading 호출",
            "healthEdit 제거 후 useRef로 setter 참조",
            "Stable Callback + Ref Pattern 적용"
        ],
        "related_notes": []
    },

    {
        "id": "onedrive-eas-android-build-permission",
        "title": "OneDrive 동기화 해제 후 EAS Android Build Permission Denied",
        "category": "build_environment",
        "tech_stack": ["Expo", "EAS Build", "Android", "Windows", "NTFS", "OneDrive"],
        "project": "smart-insole-app",
        "severity": "high",

        "symptom": (
            "OneDrive Desktop 하위에서 작업하던 프로젝트를 동기화 해제 후 로컬 경로로 옮겼는데, "
            "iOS build와 auto submit은 성공했지만 Android EAS build의 prepare project 단계에서 tar permission denied 에러가 발생했다."
        ),
        "impact": (
            "Android build가 prepare project 단계에서 실패하여 APK/AAB 생성과 배포 검증을 진행할 수 없었다."
        ),

        "timeline": [
            "OneDrive/Desktop 경로에서 프로젝트를 사용했다.",
            "OneDrive 동기화와 경로 권한 문제가 불편해 동기화를 중지했다.",
            "프로젝트를 C:/Users/kimta/Desktop 또는 C:/dev 하위로 이동했다.",
            "iOS build와 auto submit은 정상 성공했다.",
            "Android EAS build prepare project 단계에서 tar permission denied가 발생했다.",
            "Desktop 보호 폴더 문제를 의심해 C:/dev로 옮겼지만 동일하게 실패했다.",
            "로컬에서 tar -cf test.tar . 명령을 실행해 tar 자체는 성공함을 확인했다.",
            "EAS CLI의 임시 폴더 또는 TEMP/TMP 경로 문제를 의심했지만 TEMP/TMP는 정상 경로였다.",
            "파일/폴더의 NTFS 권한, ACL, 소유권 상속 구조 문제로 원인을 좁혔다.",
            "attrib, takeown, icacls 명령으로 읽기 전용 속성 제거, 소유권 재지정, 권한 상속 활성화, Full Control 재부여를 수행했다.",
            "이후 EAS Android build가 성공했다."
        ],

        "investigation_steps": [
            {
                "step": 1,
                "hypothesis": "Desktop 보호 폴더 또는 OneDrive 경로 문제일 것이다.",
                "action": "프로젝트를 C:/dev 하위로 이동하고 관리자 권한 PowerShell에서 다시 build를 시도했다.",
                "observation": "동일한 permission denied 에러가 발생했다.",
                "result": "rejected"
            },
            {
                "step": 2,
                "hypothesis": "tar 명령 자체가 권한 문제로 실패하는 것일 것이다.",
                "action": "로컬에서 tar -cf test.tar . 명령을 실행했다.",
                "observation": "로컬 tar 생성은 정상적으로 성공했다.",
                "result": "rejected"
            },
            {
                "step": 3,
                "hypothesis": "EAS CLI가 사용하는 임시 폴더 또는 TEMP/TMP 경로가 OneDrive 쪽으로 잡혀 있을 것이다.",
                "action": "TEMP/TMP 환경 변수 경로를 확인했다.",
                "observation": "TEMP/TMP는 C:/Users/Kimta/AppData/Local/Temp로 정상 설정되어 있었다.",
                "result": "rejected"
            },
            {
                "step": 4,
                "hypothesis": "OneDrive 동기화 해제 과정에서 파일/폴더의 NTFS ACL 또는 소유권 상속 구조가 꼬였을 것이다.",
                "action": "attrib -R, takeown, icacls 명령으로 읽기 전용 속성 제거, 소유권 재지정, 권한 상속 활성화, 현재 사용자 Full Control 재부여를 수행했다.",
                "observation": "권한 재설정 이후 EAS Android build가 성공했다.",
                "result": "confirmed"
            }
        ],

        "root_cause": (
            "OneDrive Desktop 리디렉션 해제 과정에서 일부 파일/폴더의 소유자 SID 또는 ACL 상속 구조가 변경되었고, "
            "같은 C: 볼륨 내 이동으로 비정상 권한 구조가 유지되면서 EAS build의 스테이징/압축 단계에서 디렉토리 생성 및 파일 접근이 실패했다."
        ),
        "solution": (
            "프로젝트 루트에서 attrib -R * /S /D로 읽기 전용 속성을 제거하고, "
            "takeown /F . /R /D Y로 소유권을 현재 사용자에게 재지정한 뒤, "
            "icacls . /inheritance:e /grant:r \"$env:USERNAME:(OI)(CI)F\" /T로 권한 상속 활성화 및 Full Control을 재부여했다."
        ),
        "structural_insight": (
            "이 문제는 결국 EAS CLI 문제가 아니라 OneDrive 리디렉션 해제 이후 유지된 Windows NTFS 권한 상속 구조 문제였다."
        ),
        "content_angle": (
            "iOS build는 되는데 Android EAS build만 prepare project 단계에서 permission denied가 날 때, "
            "빌드 도구보다 OS 파일 권한과 스테이징 과정을 의심해야 한다는 사례"
        ),
        "blog_value": 3,
        "evidence": [
            "Android EAS build prepare project 단계에서 tar permission denied 발생",
            "iOS build와 auto submit은 성공",
            "C:/dev 이동 후에도 동일 에러",
            "로컬 tar -cf test.tar . 성공",
            "TEMP/TMP 경로 정상",
            "attrib/takeown/icacls 이후 build 성공"
        ],
        "related_notes": [
            "android-cleartext-network-security-config"
        ]
    },
    {
        "id": "x-username-auth-boundary",
        "title": "X-Username 기반 사용자 식별과 JWT 인증 경계 충돌",
        "category": "authentication_design",
        "tech_stack": [
            "React-Native",
            "Expo",
            "JWT",
            "AsyncStorage",
            "REST API",
            "Authentication"
        ],
        "project": "mobile-app",
        "severity": "high",

        "symptom": (
            "iOS에서는 정상 동작하던 사용자 프로필 및 약관 조회 API가 "
            "Android에서만 404를 반환했다. "
            "/api/auth/me 는 성공하지만 /api/users/profile 과 "
            "/api/users/me/agreements 만 실패했다."
        ),

        "impact": (
            "로그인은 정상적으로 성공했지만 사용자 프로필 및 약관 상태를 "
            "불러올 수 없어 앱 초기화 흐름이 깨졌다."
        ),

        "timeline": [
            "JWT 기반 인증 구조를 사용하고 있었다.",
            "프로필 조회 API와 약관 조회 API 호출 시 X-Username 헤더를 추가로 전송하고 있었다.",
            "/api/auth/me 는 정상적으로 성공했다.",
            "Android에서만 /profile 및 /me/agreements API가 404를 반환했다.",
            "네트워크/플랫폼 차이를 의심했다.",
            "X-Username 값이 AsyncStorage 기반으로 구성된다는 점을 확인했다.",
            "여러 storage key와 trim되지 않은 문자열 가능성을 확인했다.",
            "JWT의 사용자와 X-Username 값이 불일치할 가능성에 주목했다.",
            "본인 조회 API에서는 JWT만 사용하도록 수정했다.",
            "X-Username 검증 및 전달 로직을 제거한 뒤 정상 동작했다."
        ],

        "investigation_steps": [
            {
                "step": 1,
                "hypothesis": "Android 네트워크 또는 HTTP 설정 문제일 것이다.",
                "action": "토큰 인증이 필요한 다른 API 호출 결과를 비교했다.",
                "observation": "/api/auth/me 는 정상 동작했다.",
                "result": "rejected"
            },
            {
                "step": 2,
                "hypothesis": "서버 자체의 인증 로직 또는 JWT가 잘못된 것이다.",
                "action": "JWT 인증 성공 여부와 API별 응답을 비교했다.",
                "observation": "JWT 자체는 정상이며 특정 API에서만 404가 발생했다.",
                "result": "rejected"
            },
            {
                "step": 3,
                "hypothesis": "X-Username 헤더 값이 서버의 사용자 식별 로직과 충돌하고 있을 것이다.",
                "action": "profile 및 agreements API의 요청 헤더 구조를 확인했다.",
                "observation": (
                    "JWT 기반으로 이미 사용자 식별이 가능한 API인데도 "
                    "추가로 X-Username 헤더를 보내고 있었다."
                ),
                "result": "partial"
            },
            {
                "step": 4,
                "hypothesis": (
                    "AsyncStorage에 저장된 username 값이 플랫폼별로 다르거나 "
                    "trim/legacy key 차이로 인해 JWT 사용자와 불일치하고 있을 것이다."
                ),
                "action": (
                    "getUsername()의 storage key 우선순위와 "
                    "trim 처리 여부를 확인했다."
                ),
                "observation": (
                    "Android에서 JWT 사용자와 X-Username 값이 "
                    "불일치할 가능성이 있었다."
                ),
                "result": "confirmed"
            },
            {
                "step": 5,
                "hypothesis": (
                    "본인 조회(/me, /profile)는 JWT만 사용하도록 "
                    "인증 경계를 단순화해야 한다."
                ),
                "action": (
                    "getProfile()과 getUserAgreements()에서 "
                    "X-Username 전달 및 검증 로직을 제거했다."
                ),
                "observation": (
                    "JWT 기반 사용자 식별만 사용하도록 변경 후 "
                    "Android에서도 정상 동작했다."
                ),
                "result": "confirmed"
            }
        ],

        "root_cause": (
            "JWT 기반 인증으로 이미 사용자 식별이 가능한 API에 "
            "클라이언트가 AsyncStorage 기반 X-Username 헤더를 추가로 보내면서 "
            "사용자 식별 경계가 이중화되었고, "
            "플랫폼별 storage 값 차이 또는 문자열 불일치로 인해 "
            "JWT 사용자와 X-Username 값이 충돌했다."
        ),

        "solution": (
            "/api/users/profile 및 /api/users/me/agreements 같은 "
            "본인 조회 API에서는 JWT만 사용자 식별 근거로 사용하도록 수정했다. "
            "추가적인 X-Username 헤더 전달 및 검증 로직을 제거했고, "
            "남아있는 username retrieval에는 trim 처리를 추가했다."
        ),

        "structural_insight": (
            "이 문제는 결국 Android 네트워크 문제가 아니라 "
            "클라이언트가 사용자 identity를 중복 전달하면서 발생한 "
            "인증 경계 설계 문제였다."
        ),

        "content_angle": (
            "플랫폼별 버그처럼 보였지만 실제로는 "
            "JWT identity와 client-provided identity가 충돌한 "
            "authentication boundary 설계 문제를 추적한 사례"
        ),

        "blog_value": 5,

        "evidence": [
            "/api/auth/me 는 정상 동작",
            "/profile 및 /me/agreements 에서만 404 발생",
            "X-Username 헤더 사용",
            "AsyncStorage 기반 username retrieval",
            "JWT 기반 사용자 식별과 중복",
            "X-Username 제거 후 정상 동작"
        ],

        "related_notes": [
            "android-cleartext-network-security-config"
        ]
    }
]


TROUBLESHOOTING_NOTE_BY_ID = {
    note["id"]: note for note in TROUBLESHOOTING_NOTES
}
