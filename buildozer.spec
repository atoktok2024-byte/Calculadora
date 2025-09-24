[app]

# (title)
title = Calc Lens

# (package)
package.name = com.surfassagem.app
package.domain = org.test

# (source)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# (entrypoint)
source.entrypoint = main.py

# (requirements)
requirements = python3,kivy

# (version)
version = 0.1
build = 1

# (permissions)
android.permissions = INTERNET

# (build-profile)
# A profile to use for building, either `debug` or `release`.
# Release builds require more configuration.
build_profile = debug

# (os)
# The minimum Android API level to build for.
# Higher versions are more secure and have more features, but might not be supported by older devices.
android.api = 33

# (ndk)
android.ndk = 25b

# (sdk)
android.sdk = 33.0.0

# (dist)
# This is the distribution to use.
# Recommended for a stable build.
android.dist = jammy

# (private-key)
# This is the path to your private key.
# We will use the default debug key for now.
android.release_keystore = debug.keystore
