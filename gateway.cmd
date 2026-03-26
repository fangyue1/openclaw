@echo off
rem OpenClaw Gateway (v2026.3.2)
set "TMPDIR=C:\Users\吗喽\AppData\Local\Temp"
set "PATH=C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32\OpenSSH\;C:\Program Files\dotnet\;C:\Program Files\nodejs\;C:\Program Files\Git\cmd;C:\Program Files\Tailscale\;C:\Users\吗喽\AppData\Local\Programs\Python\Python311\Scripts\;C:\Users\吗喽\AppData\Local\Programs\Python\Python311\;C:\Program Files\Google\Chrome\Application;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32\OpenSSH\;C:\Program Files\dotnet\;C:\Users\吗喽\AppData\Local\Microsoft\WindowsApps;;C:\Program Files\nodejs"
set "OPENCLAW_GATEWAY_PORT=18789"
set "OPENCLAW_GATEWAY_TOKEN=7d412070311f3fb4f0e47cc134113e26d947f234118e8e65"
set "OPENCLAW_SYSTEMD_UNIT=openclaw-gateway.service"
set "OPENCLAW_SERVICE_MARKER=openclaw"
set "OPENCLAW_SERVICE_KIND=gateway"
set "OPENCLAW_SERVICE_VERSION=2026.3.2"
"C:\Program Files\nodejs\node.exe" C:\Users\吗喽\AppData\Roaming\npm\node_modules\openclaw\dist\index.js gateway --port 18789
