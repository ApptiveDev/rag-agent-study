## **왜 고치니까 잘 됐는지 (상세 정리)**

### **1. 클라이언트가 하고 있던 일**

이전 코드는 대략 이렇게 동작했습니다.

- **`GET /api/users/profile`**
    - `Authorization: Bearer <액세스토큰>`
    - 여기에 더해 **`X-Username: <AsyncStorage에 저장된 아이디>`** 를 붙였습니다.
- **`GET /api/users/me/agreements`**
    - URL 안에 이미 **`/me/`** 가 있어서 “**지금 로그인한 나**”를 가리키는 전형적인 REST 패턴인데,
    - 마찬가지로 **`X-Username`** 을 넘기는 경우가 있었습니다 (`getUserAgreements({ username })`).

즉, **“나 자신”을 조회하는 API**인데도, **헤더로 또 한 번 “이 사용자 이름이다”라고 보내는 이중 정보**가 있었습니다.

---

### **2. 서버 입장에서 어떻게 해석될 수 있는지**

백엔드 구현에 따라 다르지만, 흔한 패턴은 다음과 같습니다.

1. **JWT만 본다**
    - 토큰 안의 `sub` / `user_id` 등으로 “누구인지” 결정하고, 그 사용자의 프로필·약관 동의를 돌려준다.
2. **`X-Username`이 있으면 그걸 우선한다 / 검증한다**
    - “헤더에 적힌 username으로 프로필을 찾는다”
    - 또는 “JWT의 사용자와 **헤더의 username이 같은지** 검사한다”
3. **불일치·잘못된 값이면 404**
    - “해당 사용자를 찾을 수 없음”으로 처리하는 API도 있습니다 (401이 아니라 404인 경우).

그래서 **토큰은 유효한데** (`/api/auth/me` 200), **프로필/약관만 404**가 나는 현상이 나올 수 있습니다.

---

### **3. 왜 iOS는 되고 안드로이드만 안 됐을 가능성이 큰지**

**같은 JS 코드**인데 한쪽만 깨지는 이유는, 보통 **“보내는 문자열이 미묘하게 다르다”** 쪽입니다.

- **`X-Username`에 실려 가는 값**은 `AsyncStorage`에서 꺼낸 `username`입니다.
- 저장 시점은 로그인 직후 `setItem('@username', trimmedUsername)` 등인데,
    - 예전에 다른 키(`username`, `@insole_app:username`)에 **다른 형태**로 저장된 값이 남았거나,
    - **앞뒤 공백**, **보이지 않는 문자**, **대소문자** 등이 OS/스토리지 구현 차이로 달라질 수 있습니다.
- `getUsername()`은 **여러 키를 순서대로** 보는데, **첫 번째로 읽힌 값**이 “로그인한 사람과 같은 사람”이 아닐 수도 있습니다.

이때:

- JWT 안의 사용자 = **방금 로그인한 계정** (서버는 이걸로 `/auth/me`는 성공)
- `X-Username` = **다른 문자열** 또는 **서버 DB에 없는 조합**

이면 서버가 “이 username으로는 프로필을 못 찾겠다” → **404**를 줄 수 있습니다.

iOS에서는 우연히 **같은 키·같은 문자열**이 잘 맞았고, 안드로이드에서는 **스토리지/키 우선순위/문자열**이 달라져서 **불일치**가 났을 가능성이 큽니다.

(재설치 후에도, 앱이 쓰는 키가 여러 개라면 **다른 경로로 예전 값이 들어가는** 경우도 생깁니다.)

---

### **4. 이번 수정이 맞는 이유 (본질적인 정리)**

| **API** | **의미** |
| --- | --- |
| `/api/users/profile` (본인 조회) | 보통 **JWT만**으로 “현재 사용자”를 특정합니다. |
| `/api/users/me/agreements` | URL의 **`me`** 가 이미 “토큰의 나”를 의미합니다. |

여기에 **`X-Username`을 추가로 보내는 것**은:

- 서버가 이를 **무시**하면 다행이지만,
- **검증/우선 적용**에 쓰이면, JWT와 **한 글자라도 어긋날 때** 이상 동작(404 등)을 유발할 수 있습니다.

그래서 이번에 한 것은:

1. **`getProfile()`**
    - **`Authorization`만** 사용 → “토큰이 가리키는 사용자”의 프로필만 조회.
    - AsyncStorage username에 의존하지 않음 → **OS별 저장값 차이**에 덜 흔들림.
2. **`getUserAgreements()`**
    - **`/users/me/...`** 는 **JWT 기준 ‘나’**만 보면 되므로 `username` 옵션(→ `X-Username`) 제거.
3. **`getUsername()`의 `trim()`**
    - 나중에 다른 API에서 `X-Username`이 필요할 때, **공백만 다른 값**으로 잘못 나가는 것을 줄이기 위한 방어.

정리하면, **문제의 핵심은 “네트워크가 안드로이드만 막혔다”가 아니라, “내 정보 조회인데 `X-Username`으로 인한 사용자 식별 불일치 가능성”**이었고, **`/me`·본인 프로필은 JWT만 쓰도록 맞춘 것**이 해결책이 된 것입니다.

- 기존 → 변경 코드
    - utils/api/profile.ts
    
    ```tsx
    export async function getProfile(): Promise<ApiResponse<GetProfileResponse>> {
      const username = await getUsername();
      if (!username) {
        throw new Error('사용자 이름을 찾을 수 없습니다.');
      }
    
      return apiGet<GetProfileResponse>(ENDPOINTS.USERS.PROFILE, {
        username,
      });
    }
    
    // 바꾼 버전
    export async function getProfile(): Promise<ApiResponse<GetProfileResponse>> {
      return apiGet<GetProfileResponse>(ENDPOINTS.USERS.PROFILE);
    ```
    
    - app/(tabs)/profile/index.tsx
    
    ```tsx
    if (foundUsername) {
                try {
                  const agreementsResponse = await getUserAgreements({ username: foundUsername });
                  if (agreementsResponse.success && agreementsResponse.data) {
                    const agreedTerms = agreementsResponse.data.agreements.filter(
                      (agreement) => agreement.agreed
                    );
                    setUserAgreements(agreedTerms);
                  }
                } catch (error) {
                  const err = error as ApiError;
                  if (err?.requiresAdditionalInfo === true && Array.isArray(err.missingFields) && err.missingFields.length > 0) {
                    setAdditionalInfoResume(err.missingFields);
                    router.replace(getFirstAdditionalInfoRoute(err.missingFields) as any);
                    return;
                  }
                  console.error('약관 동의 상태 조회 실패:', error);
                }
                
      
     // 바꾼 버전
     
     try {
                const agreementsResponse = await getUserAgreements();
                if (agreementsResponse.success && agreementsResponse.data) {
                  const agreedTerms = agreementsResponse.data.agreements.filter(
                    (agreement) => agreement.agreed
                  );
                  setUserAgreements(agreedTerms);
                }
              } catch (error) {
                const err = error as ApiError;
                if (err?.requiresAdditionalInfo === true && Array.isArray(err.missingFields) && err.missingFields.length > 0) {
                  setAdditionalInfoResume(err.missingFields);
                  router.replace(getFirstAdditionalInfoRoute(err.missingFields) as any);
                  return;
    ```
    
    - X-Username 검증 부분 제거