> 
> 
> - 원인: 일부 파일/폴더가 다른 소유자/권한 상태로 남아있어서(복사, 압축 해제, 깃/툴, 권한 상속 끊김 등) EAS가 접근 실패
> - 해결: 프로젝트 루트에 대해 **권한 상속 활성화 + 내 계정 Full Control 재부여**

ondrive/desktop 에 프로젝트 폴더 사용하다가

onedrive 동기화 되는게 귀찮고 폴더 경로에 따른 권한 에러가 많이 나서 ondrive 동기화를 중지 시킴 

하고 ondrive/desktop 에 있던 프로젝트를 c:/users/kimta/desktop 에 옮김 

ios 빌드와 auto submit 까지는 잘 됐는데 안드로이드 빌드할 때 prepare project 단계에서 경로를 못 찾는 에러 발생 (권한)

```jsx
tar: .idea/.gitignore: Cannot open: Permission denied
tar: .idea/insole-app.iml: Cannot open: Permission denied
tar: .idea/inspectionProfiles: Cannot mkdir: Permission denied
tar: .idea/misc.xml: Cannot open: Permission denied
tar: .idea/modules.xml: Cannot open: Permission denied
tar: .idea/vcs.xml: Cannot open: Permission denied
tar: .idea/workspace.xml: Cannot open: Permission denied
tar: .vscode/extensions.json: Cannot open: Permission denied
tar: .vscode/settings.json: Cannot open: Permission denied
tar: app/(tabs): Cannot mkdir: Permission denied
tar: app/account-exists.tsx: Cannot open: Permission denied
tar: app/find-account.tsx: Cannot open: Permission denied
tar: app/index.tsx: Cannot open: Permission denied
tar: app/login.tsx: Cannot open: Permission denied
tar: app/modal.tsx: Cannot open: Permission denied
tar: app/register: Cannot mkdir: Permission denied
tar: app/social: Cannot mkdir: Permission denied
```

tar 압축을 푸는 것에 대한 에러였는데 일단 권한 에러라서 desktop이 아닌 C:/dev/{프로젝트} 로 아예 C 하위로 옮겨봤다 (desktop이 보호 폴더인 경우가 많다고 지피티가 그럼)

powershell 관리자 권한으로 실행해서 다시 해봤는데 또 같은 에러로 실패 → desktop 문제 아님

`tar -cf test.tar .` ← 이 명령어로 tar 이 되는지 확인해봤는데 잘되는 것 확인 

로컬에서 permission 에러 안나니까 이제 되겠지 → eas build 시도 → but 실패

⇒ EAS CLI의 문제다! EAS가 내부적으로 다른 tar 를 쓰거나 EAS가 만드는 임시 폴더/아카이브 과정에서 권한이 막히는 것

→ EAS CLI가 프로젝트를 임시 작업 폴더에 풀어놓고(스테이징) tar 작업을 하는데 그 임시 폴더 경로가 쓰기 권한이 없는(구: onedrive 경로)곳으로 잡혀있어서 tar가 디렉토리 생성/파일 쓰기를 못 하는 상황

TEMP/TMP 경로 확인해봤더니 onedrive에 있는게  아니라 C 하위의 appdata/local에 정상으로 위치해 있음. 이게 문제가 아니고

⇒ tar 에서 permission denied가 되는게 아니라, 파일/폴더의 NTFS 권한/속성(ACL/읽기전용/소유자) 이 꼬여있는 상태

→ powershell 관리자 권한으로

1. 읽기 전용 속성 제거 `attrib -R * /S /D` 
2. 소유권을 현재 사용자로 강제 지정 `takeown /F . /R /D Y`
3. 권한을 현재 사용자 full control로 재부여 + 상속 켜기 `icacls . /inheritance:e /grant:r "$env:USERNAME:(OI)(CI)F" /T`

하고 eas build했더니 성공 

### 정리하자면

ondrive/desktop이 바탕화면에 보이게 해둔 상태에서 동기화를 끊으니까 바탕화면에 바로가기로 되어 있던 폴더나 프로그램들이 실행할 수 없다고 뜬 적이 있음 → 여기서 계정에 대한 상속 체인이 변경되었을 것으로 예측 

동기화를 끊을 시 윈도우는

- 경로 재지정을 원래 위치로 되돌리거나
- ondrive 폴더를 분리하거나
- 로컬 복사하거나 하는데

이 과정에서 내가 겪은 증상을 보자면 두가지 가능성이 있음

- 대상 경로가 바뀌어서 링크가 깨짐 (onedrive 경로 기반으로 바로가기면, 동기화 해제 시 대상이 사라져서 실행 불가)
- 파일은 있는데 접근 권한이 달라짐 (SID/ACL 문제로 엑세스 거부된 상태)

이게 eas 문제로 이어진 이유

- onedrive desktop 하위에서 생성된 파일들을
- OneDrive 리디렉션 해제 과정에서 파일/폴더의 소유자 SID 또는 ACL 상속 구조가 변경되었고,
- 이후 동일 볼륨 내 이동(C:/dev 하위)은 그 상태를 그대로 유지했을 가능성이 높다.

## 📌 문제 발생 흐름 정리

1. OneDrive가 Desktop을 리디렉션한 상태에서 프로젝트를 생성
2. OneDrive 동기화를 해제하면서:
    - Desktop 경로 재지정 해제
    - 파일 재배치/복사/분리 과정 발생
    - 이 과정에서 일부 파일의 **소유자 SID 또는 ACL 상속 체인이 변경되었을 가능성**
3. 이후 동일 C: 드라이브 내에서 `C:\dev`로 이동
    - NTFS는 같은 볼륨 이동 시 ACL을 그대로 유지
    - 즉, 이미 비정상 상태였던 권한 구조가 그대로 유지됨
4. EAS Build가 프로젝트를 스테이징하면서 디렉토리 생성/복사 단계에서 `Permission denied` 발생

---

## 📌 왜 일반 tar는 되고 EAS만 실패했을까?

- 일반 `tar`는 “읽기 중심”
- EAS는 스테이징 디렉토리 생성 + 복사 + 권한 처리 수행
- 소유자/ACL 상속 구조가 비정상이면 mkdir 단계에서 실패