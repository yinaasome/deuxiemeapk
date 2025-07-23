#!/bin/bash

# Script de correction pour les problèmes de build
echo "🔧 Correction des problèmes de build..."

# 1. Corriger les problèmes autotools
echo "📋 Installation des outils de compilation..."
sudo apt-get update
sudo apt-get install -y \
    autoconf \
    automake \
    libtool \
    autotools-dev \
    autoconf-archive \
    m4 \
    texinfo \
    help2man

# 2. Créer les liens symboliques manquants
echo "🔗 Création des liens symboliques..."
sudo ln -sf /usr/bin/aclocal /usr/bin/aclocal-1.16 2>/dev/null || true
sudo ln -sf /usr/bin/automake /usr/bin/automake-1.16 2>/dev/null || true

# 3. Définir les variables d'environnement
echo "🌍 Configuration des variables d'environnement..."
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_NDK_HOME="$HOME/.buildozer/android/platform/android-ndk-r25b"
export ANDROIDSDK="$ANDROID_HOME"
export ANDROIDNDK="$ANDROID_NDK_HOME"
export ANDROIDAPI="31"
export ANDROIDMINAPI="21"

# 4. Nettoyer les builds précédents
echo "🧹 Nettoyage des builds précédents..."
rm -rf .buildozer/android/platform/build-* 2>/dev/null || true

# 5. Vérifier les outils
echo "✅ Vérification des outils..."
echo "Autoconf version: $(autoconf --version | head -n1)"
echo "Automake version: $(automake --version | head -n1)"
echo "Python version: $(python --version)"
echo "Java version: $(java -version 2>&1 | head -n1)"

# 6. Créer main.py si inexistant
if [ ! -f main.py ]; then
    echo "📝 Création de main.py..."
    if [ -f apk3.py ]; then
        cp apk3.py main.py
        echo "✅ main.py créé à partir d'apk3.py"
    else
        cat > main.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Mobile Money - Point d'entrée principal
"""

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class MobileMoneyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Mobile Money App', font_size='20sp'))
        layout.add_widget(Label(text='Version de test', font_size='16sp'))
        return layout

if __name__ == '__main__':
    MobileMoneyApp().run()
EOF
        echo "✅ main.py minimal créé"
    fi
fi

# 7. Créer buildozer.spec simplifié si inexistant
if [ ! -f buildozer.spec ]; then
    echo "📋 Création de buildozer.spec simplifié..."
    buildozer init
    
    # Modifier le buildozer.spec pour des dépendances minimales
    sed -i 's/requirements = python3,kivy/requirements = python3==3.9.19,kivy==2.1.0,sqlite3/' buildozer.spec
    echo "✅ buildozer.spec créé et modifié"
fi

echo "🎉 Script de correction terminé !"
echo ""
echo "🚀 Vous pouvez maintenant lancer le build avec :"
echo "   buildozer android debug --verbose"
