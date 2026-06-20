## 🗂 오늘 작업

학산 QA : 시스템 폰트 사이즈 반영하지 않고 앱에서 설정한 크기 그대로 보이기 

## ⚙ 기술 / 개념

🐛 트러블슈팅

- 문제: 
`Component.defaultProps.allowFontScaling = false;`
    - 루트 파일의 해당 설정이 먹지 않음
- 과정
    - https://github.com/facebook/react-native/issues/51113?utm_source=chatgpt.com → index.js에서 해당 설정이 특정 환경에서 먹히지 않는 케이스 다수 발생
    - 적용 타이밍/엔트리포인트 문제 또는 일부 RN 버전/신 아키텍처 관련 이슈 의심
        - 엔트리포인트 : index.js 생성 후에 메인엔트리를 index.js 로해서 
        index.js → expo runtime → expo router 초기화 → app/_layout.tsx 
        이렇게 했지만 defaultProps 방식 여전히 안 먹음
        
        ```jsx
        import { Text, TextInput } from "react-native";
        
        Text.defaultProps = Text.defaultProps || {};
        Text.defaultProps.allowFontScaling = false;
        Text.defaultProps.maxFontSizeMultiplier = 1;
        
        TextInput.defaultProps = TextInput.defaultProps || {};
        TextInput.defaultProps.allowFontScaling = false;
        TextInput.defaultProps.maxFontSizeMultiplier = 1;
        
        // 그 다음 expo-router 실행
        import "expo-router/entry";
        ```
        
    - 런타임이 아닌 컴파일 타임 치환 방식을 사용하자! (공장에서 조립하기 전에 부품 자체를 바꿔 끼워 생산하는 것)
        - Text.defaultProps 는 RN이 가진 Text라는 객체의 속성을 런타임에 수정하는 건데 Text가 아닌 AppText로 코드를 바꾸면 RN 내부 구조나 Fabric 영향 없이 안정적으로 적용할 수 있음
    - AppHeader의 텍스트에서는 시스템 설정에 영향을 받지 않음 (allowFontScaling = false 로 되어 있기 때문에)
- 원인: iOS/Android/Expo 정책 때문이 아니고 엔트리포인트도 아니고 RN 최신 구조에서의 전역 defaultProps 패치가 더 이상 안전하지 않은 것.
    
    ⇒ 전역 defaultProps로 Text를 막는 방식은 공식적으로 보장되지 않는다. 
    
- 해결: AppText 래퍼 만들어서 전부 교체하기,,