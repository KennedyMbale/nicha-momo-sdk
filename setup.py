from setuptools import setup, find_packages

setup(
    name="nicha_momo",
    version="1.2.0",
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    author="Kennedy Mbale",
    author_email="kennedymbale4@gmail.com",
    description="Complete MTN Mobile Money API Integration [sandbox]",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KennedyMbale/nicha-momo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)