[app]

title = Mobile Money
package.name = mobilemoney
package.domain = com.mobilemoney.app

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
source.exclude_exts = spec
source.exclude_dirs = tests, bin, venv, __pycache__, .git, .github

version = 1.0

requirements = python3==3.9.19,kivy==2.1.0,sqlite3,pandas==1.5.3,matplotlib==3.6.3,numpy==1.24.4,openpyxl==3.1.2,pillow==9.5.0,plyer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK

android.api = 31
android.minapi = 21

# Fichier : buildozer.spec

# Version NDK actuelle (minimum requis par python-for-android)
android.ndk = 25b

# Chemin vers le NDK (cohérent avec celui du script ci-dessus)
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# Désactiver la mise à jour du SDK automatiquement
p4a.skip_update = True
p4a.accept_sdk_license = True

# Branch principale pour éviter les versions anciennes
p4a.branch = master

# ❌ Supprimé les chemins forcés pour que Buildozer télécharge proprement
# android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
# android.sdk_path = ~/.buildozer/android/platform/android-sdk

android.enable_androidx = True
android.archs = arm64-v8a,armeabi-v7a
android.no_byte_compile_python = False
android.entrypoint = org.kivy.android.PythonActivity
android.activity_class_name = org.kivy.android.PythonActivity
android.service_class_name = org.kivy.android.PythonService
android.apptheme = "@android:style/Theme.NoTitleBar"
android.copy_libs = 1

p4a.skip_update = True
p4a.accept_sdk_license = True
p4a.bootstrap = sdl2
android.debug_artifact = apk
p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1

# (optionnel) pour forcer les chemins de sortie
# build_dir = ./.buildozer
# bin_dir = ./bin
