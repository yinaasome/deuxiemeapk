[app]
title = MonApp
package.name = monapp
package.domain = org.monorganisation
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_path = /home/runner/.buildozer/android/platform/android-sdk/ndk/25.1.8937393
android.sdk = 24
android.ndk_api = 21
android.archs = armeabi-v7a, arm64-v8a
