title = Mobile Money Manager
package.name = mobilemoneymanager
package.domain = org.mobilemoney
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.3.1,sqlite3,pandas,matplotlib,numpy,pillow,plyer,openpyxl,cython
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,WAKE_LOCK
android.archs = arm64-v8a, armeabi-v7a
android.logcat_filters = *:S python:D
p4a.fork = kivy
p4a.branch = develop
p4a.bootstrap = sdl2
android.java_path = /usr/lib/jvm/java-11-openjdk-amd64  ← à ajouter si `javac` introuvable
