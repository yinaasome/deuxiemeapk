[app]

title = MobileMoney
package.name = mobilemoney
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,db
version = 1.0
requirements = python3,kivy,pandas,numpy,matplotlib,plyer
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Spécification du SDK/NDK/API
android.api = 33
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21
android.gradle_dependencies = androidx.appcompat:appcompat:1.1.0

# Options supplémentaires
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

# (facultatif)
#android.arch = armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1
