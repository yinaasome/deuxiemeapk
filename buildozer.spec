[app]
title = MonApp
package.name = monapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv
version = 0.1
requirements = python3,kivy
orientation = portrait

[buildozer]
log_level = 2

[android]
android.api = 31
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.ndk_api = 21
android.ndk_path = /home/runner/.buildozer/android/platform/android-sdk/ndk/25.1.8937393
