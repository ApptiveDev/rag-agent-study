### 에러 로그

```jsx
pgAdmin Runtime Environment
--------------------------------------------------------
Python Path: "C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe"
Runtime Config File: "C:\Users\Kimta\AppData\Roaming\pgadmin4\config.json"
Webapp Path: "C:\Program Files\PostgreSQL\18\pgAdmin 4\web\pgAdmin4.py"
pgAdmin Command: "C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe -s C:\Program Files\PostgreSQL\18\pgAdmin 4\web\pgAdmin4.py"
Environment: 
  - ALLUSERSPROFILE: C:\ProgramData
  - ANDROID_HOME: C:\Users\Kimta\AppData\Local\Android\Sdk
  - APPDATA: C:\Users\Kimta\AppData\Roaming
  - CommonProgramFiles: C:\Program Files\Common Files
  - CommonProgramFiles(x86): C:\Program Files (x86)\Common Files
  - CommonProgramW6432: C:\Program Files\Common Files
  - COMPUTERNAME: TAERAN
  - ComSpec: C:\WINDOWS\system32\cmd.exe
  - Desktop: C:\Users\Kimta\Desktop
  - DriverData: C:\Windows\System32\Drivers\DriverData
  - EFC_18504_1262719628: 1
  - EFC_18504_1592913036: 1
  - EFC_18504_2283032206: 1
  - EFC_18504_2775293581: 1
  - EFC_18504_3789132940: 1
  - ELECTRON_ENABLE_SECURITY_WARNINGS: false
  - FPS_BROWSER_APP_PROFILE_STRING: Internet Explorer
  - FPS_BROWSER_USER_PROFILE_STRING: Default
  - HOMEDRIVE: C:
  - HOMEPATH: \Users\Kimta
  - JAVA_HOME: C:\Program Files\Android\Android Studio\jbr
  - LOCALAPPDATA: C:\Users\Kimta\AppData\Local
  - LOGONSERVER: \\TAERAN
  - NUMBER_OF_PROCESSORS: 16
  - NVM_HOME: C:\nvm
  - NVM_SYMLINK: C:\nvm4w\nodejs
  - OneDrive: C:\Users\Kimta\OneDrive
  - ORIGINAL_XDG_CURRENT_DESKTOP: undefined
  - OS: Windows_NT
  - Path: C:\Program Files\PostgreSQL\18\pgAdmin 4\runtime;C:\nvm4w\nodejs;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;C:\Users\Kimta\AppData\Local\Android\Sdk\platform-tools;C:\nvm;C:\nvm;C:\Program Files\PostgreSQL\18\bin;C:\Users\Kimta\OneDrive\Desktop\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin;C:\Users\Kimta\AppData\Local\Programs\Python\Python310\Scripts\;C:\Users\Kimta\AppData\Local\Programs\Python\Python310\;C:\Users\Kimta\AppData\Local\Programs\Python\Python311\Scripts\;C:\Users\Kimta\AppData\Local\Programs\Python\Python311\;C:\Users\Kimta\AppData\Local\Programs\Python\Launcher\;C:\nvm4w\nodejs;C:\Users\Kimta\AppData\Local\Microsoft\WindowsApps;C:\Users\Kimta\AppData\Local\Android\Sdk\platform-tools;C:\Users\Kimta\AppData\Local\Android\Sdk\emulator;C:\Users\Kimta\AppData\Local\Android\Sdk\tools;C:\Users\Kimta\AppData\Local\Android\Sdk\tools\bin;C:\nvm;C:\nvm;C:\Users\Kimta\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\Kimta\AppData\Local\Programs\cursor\resources\app\bin;C:\Users\Kimta\OneDrive\Desktop\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin;
  - PATHEXT: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC
  - PGADMIN_INT_KEY: 42071496-44f8-44fa-b5cb-1901b1b3cfe6
  - PGADMIN_INT_PORT: 63414
  - PGADMIN_SERVER_MODE: OFF
  - PROCESSOR_ARCHITECTURE: AMD64
  - PROCESSOR_IDENTIFIER: Intel64 Family 6 Model 154 Stepping 3, GenuineIntel
  - PROCESSOR_LEVEL: 6
  - PROCESSOR_REVISION: 9a03
  - ProgramData: C:\ProgramData
  - ProgramFiles: C:\Program Files
  - ProgramFiles(x86): C:\Program Files (x86)
  - ProgramW6432: C:\Program Files
  - PSModulePath: C:\Program Files\WindowsPowerShell\Modules;C:\WINDOWS\system32\WindowsPowerShell\v1.0\Modules
  - PUBLIC: C:\Users\Public
  - SESSIONNAME: Console
  - SystemDrive: C:
  - SystemRoot: C:\WINDOWS
  - TEMP: C:\Users\Kimta\AppData\Local\Temp
  - TMP: C:\Users\Kimta\AppData\Local\Temp
  - USERDOMAIN: TAERAN
  - USERDOMAIN_ROAMINGPROFILE: TAERAN
  - USERNAME: Kimta
  - USERPROFILE: C:\Users\Kimta
  - windir: C:\WINDOWS
  - ZES_ENABLE_SYSMAN: 1
--------------------------------------------------------

Total spawn time to start the pgAdmin4 server: 0.008 Sec
2026-02-26 15:38:31,689: WARNING	werkzeug:	Werkzeug appears to be used in a production deployment. Consider switching to a production web server instead.

 * Serving Flask app 'pgadmin'
 * Debug mode: off

------------------------------------------
Total time taken to ping pgAdmin4 server: 93.901 Sec
------------------------------------------
Total launch time of pgAdmin4: 94.51 Sec
------------------------------------------
Application Server URL: http://127.0.0.1:63414/?key=42071496-44f8-44fa-b5cb-1901b1b3cfe6
2026-02-26 15:38:55,467: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:39:02,277: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:39:05,024: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:39:08,378: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:39:14,702: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:14,721: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:14,833: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:39:18,532: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:24,923: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:28,864: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:49,206: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:39:49,318: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:50,895: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:51,008: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:52,414: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:52,434: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:52,550: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:52,823: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:52,917: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:53,019: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:53,021: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:53,128: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:39:53,169: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:53,298: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:39:57,466: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:40:12,523: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:40:12,634: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:40:17,615: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:42:28,077: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:42:28,901: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:42:29,090: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:42:52,529: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:42:53,001: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:42:55,111: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:42:59,965: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:00,259: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:00,259: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:00,583: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:00,690: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:00,799: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:03,945: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:04,526: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:09,928: ERROR	pgadmin:	Failed to execute query (execute_async) for the server #3 - CONN:3449827(Query-id: 200001):
Error Message:ERROR:  consuming input failed: SSL connection has been closed unexpectedly 

2026-02-26 15:43:10,068: ERROR	pgadmin:	Failed to execute query (execute_async) for the server #3 - CONN:428388(Query-id: 268034):
Error Message:ERROR:  consuming input failed: SSL connection has been closed unexpectedly 

2026-02-26 15:43:10,160: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:10,759: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:13,475: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:14,207: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:14,240: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:14,273: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:5900114 (Query-id: 5116705):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:14,391: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:43:14,509: ERROR	pgadmin:	Failed to execute query (execute_async) for the server #3 - CONN:6008019(Query-id: 1615208):
Error Message:ERROR:  consuming input failed: SSL connection has been closed unexpectedly 

2026-02-26 15:43:14,652: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:15,016: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:15,208: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:15,423: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:15,672: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:43:16,669: ERROR	pgadmin:	Failed to execute query (execute_async) for the server #3 - CONN:5372890(Query-id: 7718987):
Error Message:ERROR:  consuming input failed: SSL connection has been closed unexpectedly 

2026-02-26 15:43:18,301: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:43:18,328: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:18,846: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:43:19,543: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:20,159: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:21,648: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:22,734: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:43:22,826: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:43:23,426: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:24,613: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:43:25,099: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  "uwellnow" 데이터베이스 없음

2026-02-26 15:43:25,403: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:43:25,784: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:43:26,607: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:9510520 (Query-id: 9621522):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:27,594: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:43:27,648: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:43:28,695: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:28,859: ERROR	pgadmin:	Could not find the specified database.

2026-02-26 15:43:29,225: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:29,596: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:29,730: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:29,843: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:29,935: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:30,139: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:30,201: ERROR	pgadmin:	connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5433', hostaddr: '::1': connection timeout expired
- host: 'localhost', port: '5433', hostaddr: '127.0.0.1': connection timeout expired

2026-02-26 15:43:30,341: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:30,370: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:30,472: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:3376031 (Query-id: 5432376):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:30,488: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:30,559: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:30,683: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: fe_sendauth: no password supplied
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: fe_sendauth: no password supplied

2026-02-26 15:43:31,387: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:31,815: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:8838435 (Query-id: 421063):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:31,848: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:7618602 (Query-id: 8882867):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:31,867: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:32,066: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:32,138: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:6847692 (Query-id: 4360272):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:32,521: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:32,647: ERROR	pgadmin:	connection failed: connection to server at "35.227.164.209", port 5432 failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:34,294: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:436281 (Query-id: 8485337):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:34,296: ERROR	pgadmin:	Failed to execute query (execute_2darray) for the server #3 - CONN:1575895 (Query-id: 8881322):
Error Message:consuming input failed: SSL connection has been closed unexpectedly

2026-02-26 15:43:40,973: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.

2026-02-26 15:43:43,750: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.

2026-02-26 15:43:43,848: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.

2026-02-26 15:43:43,993: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.

2026-02-26 15:43:45,750: ERROR	pgadmin:	connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: 치명적오류:  최대 동시 접속자 수를 초과했습니다.

```

### 문제 상황

- 치명적 오류: 최대 동시 접속자 수를 초과했습니다.
→ max_connections 한도 초과 (커넥션을 많이 열었거나, 닫혔는데도 세션이 남아있거나, pgadmin이 재시도 폭주)
- “uwellnow” 데이터베이스 없음 → Could not find the specifed database
→ pgadmin 서버 등록에서 ‘maintenance DB’ 또는 기본 DB가 uwellnow로 되어 있는데, 실제 로컬 Postgres에 그 DB가 없음
- fe_sendauth: no password supplied → 인증 필요한데 비번 입력 안된 상태에서 재시도 계속
- 35.227.164.209 … SSL connection has been closed unexpectedly → 원격 DB 쪽 SSL 설정/네트워크 문제로 원격도 계속 재시도

⇒ 합쳐져서 폭주 더 심해짐 

### 트러블슈팅

- 최종 원인
    - pgadmin에 등록된 서버 중 하나가 존재하지 않는 db를 기본 db (maintenance DB)로 들고 있음
    - fe_sendauth: no password supplied → pgadmin이 비번을 못 가져오거나 저장 안 함
    - 5433 포트 나오는 거 봐서 등록된 서버 여러 개고 그 중 하나가 5433
- 시도
    - pgadmin 관련 워커 작업 끝내기 → postgres 서비스 재시작 ⇒ 소용 없음 (uwellnow 디비를 자꾸 찾으려고 함)
        - postgres=# select usename, datname, application_name, count(*) from pg_stat_activity group by 1,2,3 order by 4 desc; → psql에서 현재 붙어있는 연결 보기 (pgadmin 다라락 찍히면 폭주하는 거 맞음)
        - pg_stat_activity 겨과 보면 pgadmin 폭주로 db 커넥션 쌓이는 거 아님
            - psql 1개 말고 application_name 비어있는 거 8개 뿐임. 본체는 postgres가 문제가 아니라 pgadmin 쪽 로컬 설정/자격증명/등록 서버 꼬여서 에러 반복하는 것
- 해결
    - dbeaver로 갈아탔음 → 버벅임 없고 완전 편안

### 인사이트

DBeaver과 PgAdmin의 공통점

- libpq 프로토콜 (TCP/IP)로 서버에 접속함

Pgadmin : PostgreSQL 전용 공식 툴

- PgAdmin → PostgreSQL driver → PostgreSQL server 구조인데
- replication, vacuum, extension, role 관리, pg_stat 관련 기능에서 postgre 기능에 최적화되어 있다
- 내부가 웹앱 구조 : Electron/Browser UI → Python backend (Flask) → DB 연결
    - 느릴 수 있고
    - 메모리 많이 먹고
    - 로딩 버벅임 있음

DBeaver : 범용 DB 툴

- Dbeaver(Java desktop app) → JDBC driver → postgreSQL server 구조인데
- PostgreSQL JDBC driver로 연결하기 때문에
    - Java 기반
    - 연결 속도 빠름
    - 안정적
- 모든 DB 지원

DBeaver이 더 안정적인 이유

> 레이어 수 + 실행 방식 + 프로토콜 처리 방식 차이
> 

단순히 Java 라서가 아니라 중간계층이 훨씬 적고 직접 DB driver를 호출하는 구조임.

PgAdmin은

```bash
Browser / Electron UI
        ↓
Python Flask backend
        ↓
psycopg driver
        ↓
libpq
        ↓
PostgreSQL
```

UI ↔ backend 통신이 있는 반면, (레이어가 한 개 더 있는 것)

DBeaver은

```bash
Java Desktop App
        ↓
PostgreSQL JDBC driver
        ↓
PostgreSQL
```

바로 DB driver를 호출하는 구조이다. (중간에 백엔드가 없음) 

PgAdmin은 Python backend 에서 crash가 날 수 있다 (내가 겪은 흰 화면이 이런 경우)

connection pool 이 제한에 도달했다거나 하는 면에서 백엔드 서버가 터질 수 있음