[app]

# (str) Title of your application
title = Calculadora de Curvas

# (str) Package name
package.name = com.example.calculadora

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Application version
version = 1.0.0

# (list) Application requirements
# android.api = 33
requirements = python3, kivy, Pillow

# (str) Path to the main file of your application
source.dir = .

# (str) Main application file
main.py = main.py

# (list) Permissions
android.permissions = INTERNET

# (bool) If you use a custom icon, use this property to specify it
# icon.filename = %(source.dir)s/icon.png

# (list) If you use a custom splash screen, use this property to specify it
# splash.filename = %(source.dir)s/splash.png

[buildozer]

# (int) The Android api level to use
android.api = 33

# (int) The minimum Android api level to use
android.min_api = 21

# (int) The target Android api level to use
android.target_sdk = 33

# (str) The Android NDK version to use
android.ndk = 25b

# (str) The Java version to use
android.java_source_version = 1.8

# (str) The Ant version to use
android.ant_version = 1.9.1

# (str) The Android build tools version to use
android.build_tools = 33.0.0
