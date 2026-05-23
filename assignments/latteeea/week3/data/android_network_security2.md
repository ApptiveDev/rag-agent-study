개발중인 서버가 ssl 을 붙이지 못해서 https가 아닌 http로 운영되고 있고

react native expo 및 eas build 로 android와 ios 동시 빌드를 하고 있다면

android 의 네이티브 network config 설정이 필요함

android 9+ 이상부터는 HTTP를 기본적으로 차단하기 때문에 이를 풀어주지 않으면 apk 파일로 다운받았을때 

서버에 연결할 수 없습니다. ([https://15.~~~](https://15.~~~/)) 실제 기기를 사용하는 경우 컴퓨터의 로컬 IP 주소를 사용해야 합니다. 예:[http://192~~](http://192~~/)

이러한 에러가 나옴 

이때 HTTP로 테스트하기 위해서는 network_security_config / usesCleartextTraffic이 필요함 

- app.json에 http 허용 켜기 (usesCleartextTraffic: true)
    
    ```jsx
    {
      "expo": {
        "android": {
          "usesCleartextTraffic": true
        }
      }
    }
    ```
    
- network_security_config.xml 만들기
    
    ```jsx
    <?xml version="1.0" encoding="utf-8"?>
    <network-security-config>
      <base-config cleartextTrafficPermitted="true" />
    </network-security-config>
    
    ```
    
- android manifest의 application 태그에 연결하기
    
    ```jsx
    android:usesCleartextTraffic="true"
    
    android:networkSecurityConfig="@xml/network_security_config"
    ```
    

이걸 하고 바로 prebuild를 다시 돌리면 androidmanifest 가 덮어씌워질 수 있음 이걸 방지하기 위해서 config plugin 을 통해 빌드 때마다 자동 주입되게 만드는 방법이 있음 

```jsx
const { withAndroidManifest, withDangerousMod } = require("@expo/config-plugins");
const fs = require("fs");
const path = require("path");

module.exports = function withNetworkSecurityConfig(config) {
  // 1) res/xml/network_security_config.xml 생성/갱신
  config = withDangerousMod(config, [
    "android",
    async (cfg) => {
      const projectRoot = cfg.modRequest.projectRoot;
      const xmlDir = path.join(projectRoot, "android", "app", "src", "main", "res", "xml");
      const xmlPath = path.join(xmlDir, "network_security_config.xml");

      fs.mkdirSync(xmlDir, { recursive: true });

      const xml = `<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
  <base-config cleartextTrafficPermitted="true" />
</network-security-config>
`;
      fs.writeFileSync(xmlPath, xml, "utf8");
      return cfg;
    },
  ]);

  // 2) AndroidManifest.xml application에 속성 강제 주입
  config = withAndroidManifest(config, (cfg) => {
    const app = cfg.modResults.manifest.application?.[0];
    if (app) {
      app.$["android:usesCleartextTraffic"] = "true";
      app.$["android:networkSecurityConfig"] = "@xml/network_security_config";
    }
    return cfg;
  });

  return config;
};

```

ios에서는 기본적으로 차단을 안하나? ios에서는 서버 연결 잘 된 이유

- 기본적으로 보안 안된 HTTP를 막긴 함
- 하지만 나는 iOS에서 NSExceptionDomains에 http ip 주소를 넣어놨고 NSExceptionAllowsInsecureHTTPLoads : true 로 HTTP 예외를 허용해둔 상태
- android 에서는 cleartext 트래픽을 차단하는 정책이 생겼고
- iOS처럼 info.plist 한 덩어리로 예외가 잡히는게아니라 usesCleartextTraffic, network_security_config 같은걸로 명시적 허용 필요

### 정리하자면

- iOS에서는 NSExceptionDomains로 예외 허용해놨고 (app.json)
- android 에서는 app.json 말고도 네이티브 폴더에 설정되어야 하는 파일이 있는데 prebuild를 할때 없어져버려서 에러가 다시 생긴 거임