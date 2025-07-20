[app]
title = MobileMoney
package.name = mobilemoney
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,plyer,pandas,numpy,matplotlib,sqlite3
orientation = portrait

# (optionnel) inclure le fichier de base de données si tu veux l’ajouter par défaut
# presplash.filename = %(source.dir)s/data/logo.png

fullscreen = 1
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.ndk = 25b
android.ndk_api = 21
android.minapi = 21
android.arch = armeabi-v7a
android.packaging = zip
android.gradle_dependencies = 
android.manifest.intent_filters =

# Pour matplotlib
android.add_runnable_pip_install_options = true

# Inclure les fichiers supplémentaires comme les .kv ou autres si séparés
# source.include_patterns = *.py, *.kv

[buildozer]
log_level = 2
warn_on_root = 1
