[app]

# (str) Title of your application
title = Mobile Money App

# (str) Package name
package.name = mobilemoneyapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test
# (str)
source.dir = .
# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Requirements (a.k.a. installed python packages)
# You must specify the exact version for some packages, otherwise it might fail.
requirements = python3,kivy,sqlite3,hashlib,datetime,pandas,matplotlib,numpy,plyer

# (str) Orientation of your app: 'all', 'landscape', 'portrait'
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Android API target (default is 27)
android.api = 33

# (int) Minimum Android API required (default is 21)
android.minapi = 21

# (str) Android NDK version (default is 19b)
android.ndk = 25b

# (str) Android SDK version (default is 20)
android.sdk = 29

# (str) Android NDK path (if not in your PATH)
# android.ndk_path = /opt/android-ndk-r25b

# (str) Android SDK path (if not in your PATH)
# android.sdk_path = /opt/android-sdk

# (str) Python for android path (if not in your PATH)
# python.for.android = /opt/python-for-android

# (str) The directory where the buildozer files are stored
# buildozer.dir = .buildozer

# (str) The directory where the output packages are stored
# bin_dir = bin

# (list) Source files to include (relative to the main.py file)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude (relative to the main.py file)
# source.exclude_dirs = tests,bin

# (str) Log level (0 = error, 1 = warning, 2 = info, 3 = debug)
log_level = 2

# (bool) If set to 1, the app will be built in debug mode
debug = 0

# (list) Add your own Java files to the build
# android.add_src = path/to/your/Java/files

# (list) Add your own C files to the build
# android.add_libs_armeabi_v7a = path/to/your/C/files

# (list) Add your own assets to the build
# android.add_assets = path/to/your/assets

# (str) Icon file
icon.filename = icon.png

# (str) Splash screen file
# splash.filename = splash.png

# (str) Path to the AndroidManifest.xml file
# android.manifest = AndroidManifest.xml

# (bool) If set to 1, the app will be signed with a debug key
# android.release = 0

# (str) Keystore file for signing
# android.keystore = ~/.android/debug.keystore

# (str) Keystore password for signing
# android.keystore.pass = android

# (str) Key alias for signing
# android.keyalias = androiddebugkey

# (str) Key alias password for signing
# android.keyalias.pass = android
