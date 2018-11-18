from setuptools import find_packages, setup

from guitarlette.__version__ import __version__


def get_long_description():
    return open("README.md", "r", encoding="utf8").read()


setup(
    name="guitarlette",
    version=__version__,
    packages=find_packages(),
    license="MIT",
    url="https://github.com/erm/guitarlette",
    description="A lightweight songwriting tool for guitar.",
    long_description=get_long_description(),
    install_requires=["starlette", "uvicorn", "asyncpg", "graphene", "pychord"],
    long_description_content_type="text/markdown",
    author="Jordan Eremieff",
    author_email="jordan@eremieff.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
