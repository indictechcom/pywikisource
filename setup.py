import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywikisource",
    version="0.0.4",
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
        'aiohttp'
    ],
    setup_requires=['wheel'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)