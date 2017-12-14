from setuptools import setup

setup(
    name='bpslibrary',
    package=['bpslibrary'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_bcrypt',
        'flask_login',
        'flask_wtf',
        'numpy',
        'pillow',
        'pyisbn',
        'sqlalchemy',
        'uwsgi',
        'wtforms',
        'zbar_py',
    ],
)
