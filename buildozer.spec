[app]

# Titre de l'application
title = Mobile Money

# Nom du package (doit être unique)
package.name = mobilemoney

# Domaine du package (convention inversée)
package.domain = org.orange

# Version de l'application (format: 1.2.0)
version = 1.0.0

# Configuration de l'APK
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25.2.9519653
android.sdk = 33
android.gradle_dependencies = 'com.android.tools.build:gradle:7.2.2'
android.allow_backup = False
android.arch = armeabi-v7a

# Configuration de la compilation
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
requirements = python3==3.9.*,kivy==2.3.0,plyer,sqlite3,pandas,matplotlib,numpy,openpyxl
orientation = portrait
fullscreen = 0

# Options de build
log_level = 2
android.accept_sdk_license = True
p4a.branch = master

# Configuration Kivy
kivy.graphics = opengl, sdl2
kivy.window = sdl2

# Icones et presse-papiers
icon.filename = %(source.dir)s/data/icon.png
presplash.filename = %(source.dir)s/data/presplash.png

# Configuration release
# (commenté par défaut - à décommenter pour les builds de production)
#[buildozer]
#log_level = 2
#android.debug = 0
#android.release_artifact = .apk
