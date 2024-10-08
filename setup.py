import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywikisource",
    version="0.0.5",
    author="Jay Prakash",
    author_email="0freerunning@gmail.com",
    description="Wikisource Dedicated Python API library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/indictechcom/pywikisource",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'bs4',
        'asyncio',
        'aiohttp',
        'typing-extensions'# included typing-extensions for python 3.6, typing is best for strictly python>= 3.9
    ],
    python_requires='>=3.6',
    setup_requires=['wheel'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
