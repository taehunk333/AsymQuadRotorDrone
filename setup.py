from setuptools import setup, find_packages

setup(
    name = "aqrdrone_312",
    version = "0.0.1",
    packages = find_packages(),
    description = "A Python package for simulating the dynamics of an asymmetric quad rotor drone and designing it.",
    author = 'Taehun Kim',
    maintainer_email = 'tk6at@virginia.edu',
    install_requires = [],
    python_requires = '>=3.12',
    include_package_data = True
)