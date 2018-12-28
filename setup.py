from setuptools import setup
from jrnl.version import DESCRIPTION, PYPINAME, VERSION


# Parse readme to include in PyPI page
with open("README.md") as f:
    long_description = f.read()


def capitalize(s):
    """Capitalize the first letter of a string.

    Unlike the capitalize string method, this leaves the other
    characters untouched.
    """
    return s[:1].upper() + s[1:]


setup(
    name=PYPINAME,
    version=VERSION,
    description=capitalize(DESCRIPTION),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mwiens91/jrnl",
    author="Matt Wiens",
    author_email="mwiens91@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
    ],
    data_files=[("/usr/local/man/man1", ["man/jrnl.1"])],
    packages=["jrnl"],
    entry_points={"console_scripts": ["jrnl = jrnl.main:main"]},
    python_requires=">=3.5",
    install_requires=["python-dateutil", "PyYAML"],
)
