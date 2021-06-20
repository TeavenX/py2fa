from setuptools import setup

APP = ['py2fa.py']
DATA_FILES = ['statics']
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'py2fa.icns',
    'plist': {
        'CFBundleShortVersionString': '0.0.1',
        'CFBundleName': "PY2FA",
        'CFBundleDisplayName': "PY2FA",
        'CFBundleGetInfoString': "验证码全局提取工具",
        'CFBundleIdentifier': "xyz.teaven.py2fa",
        'CFBundleVersion': "0.0.1",
        'NSHumanReadableCopyright': "版权所有 © 2021, teaven.xyz",
        'Localization native development region':'China',
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    app=APP,
    name='PY2FA',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)