from setuptools import setup, find_packages

setup(
    name="frmpd",
    version="0.1.0",
    description="A Tool for Multiple Protocols Debug",
    author="fishros",
    author_email="fishros@foxmail.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'frmpd': ['templates/*.html'],
    },
    install_requires=[
        "Flask>=2.0.0",
        "pyserial",
        "flask-socketio",
        "eventlet",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "frmpd=frmpd.cli:main"
        ]
    },
)