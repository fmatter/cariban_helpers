import setuptools

setuptools.setup(
    name="cariban_helpers",
    version="0.0.1",
    author="Florian Matter",
    author_email="florianmatter@gmail.com",
    description="Cariban languages data for CLDF projects",
    url="https://github.com/fmatter/cariban_helpers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': ['cmeta_download=cariban_helpers.download:main'],
    },
    python_requires='>=3.6',
)
