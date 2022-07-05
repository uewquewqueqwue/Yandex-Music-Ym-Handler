from setuptools import setup, find_packages

requirements = [
    "rich ~= 12.4.4",
    "braillert ~= 2.0.1",
    "colorama ~= 0.4.4",
    "pillow ~= 9.1.1",
    "aiohttp ~=  3.7.4.post0",
]


setup(
    name="YmHandler",
    version="1.14.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    author="uewquewqueqwue",
    author_email="qdissh@gmail.com",
    install_requires=requirements,
    url="https://github.com/uewquewqueqwue/Ym-Handler",
    license="MIT",
    entry_points={
        "console_scripts": [
            "ymhandler = ymhandler.main:main",
        ],
    },
)
