[app]

# (str) Title of your application
title = Mobile Money

# (str) Package name
package.name = mobilemoney

# (str) Package domain (needed for android/ios packaging)
package.domain = com.mobilemoney.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, __pycache__, .git, .github

# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# Dépendances minimales pour éviter les conflits
requirements = python3==3.9.19,kivy==2.1.0,sqlite3,pandas==1.5.3,matplotlib==3.6.3,numpy==1.24.4,openpyxl==3.1.2,pillow==9.5.0,plyer

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path = ~/.buildozer/android/platform/android-sdk

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
android.enable_androidx = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (bool) Skip byte compile for .py files
android.no_byte_compile_python = False

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
android.activity_class_name = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
android.service_class_name = org.kivy.android.PythonService

# (str) Android app theme, default is ok for Kivy-based app
android.apptheme = "@android:style/Theme.NoTitleBar"

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (bool) If True, then skip trying to update the Android sdk
p4a.skip_update = True

# (bool) If True, then automatically accept SDK license
p4a.accept_sdk_license = True

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# (str) The format used to package the app for debug mode (apk).
android.debug_artifact = apk

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

# (str) The directory in which python-for-android should look for your own build recipes
# p4a.local_recipes = ./p4a-recipes

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
