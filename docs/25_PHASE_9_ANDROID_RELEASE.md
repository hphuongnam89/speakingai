# Phase 9 Android release contract

Android gửi Bearer token và `X-Profile-Id` qua OkHttp interceptor; profile selector không được dùng làm identity. HTTP 401 xóa token trong memory để UI có thể đưa người dùng về login, còn timeout/permission errors phải hiển thị retry path ở ViewModel/UI.

Release bật minify và tắt cleartext traffic; debug mới cho phép cleartext để dùng emulator/LAN. Signing chỉ lấy từ `ANDROID_KEYSTORE_PATH`, `ANDROID_KEYSTORE_PASS`, `ANDROID_KEY_ALIAS` và `ANDROID_KEY_PASSWORD`, không commit keystore/secrets. Release logging interceptor là `NONE`, không log transcript, audio hoặc token.

Chạy `scripts/check-android.ps1` sau khi cài Gradle wrapper. Cần kiểm tra thêm trên emulator và thiết bị thật: microphone permission, rotation/process death, logout, expired token, 401, timeout và background recording.
