import setuptools
import aaschema

VERSION = aaschema.__version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aaschema",
    version=VERSION,
    python_requires=">=3.6",
    author="Loo Zheng Yuan",
    author_email="loozhengyuan@gmail.com",
    description="Schema utility for Adobe Analytics data feeds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
    ],
    extras_require={
        "setup": [
            "requests",
            "beautifulsoup4",
            "lxml",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
