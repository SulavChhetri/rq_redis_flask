from setuptools import setup
from setuptools import find_packages
setup(
    name="docker",
    version="1.0.0",
    description="This is a simple web application implemented using flask and implemented using docker",
    author="Sulav",
    packages=find_packages(),
    install_requrires=['redis','rq']
    )