import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    raise RuntimeError("analyticord requires the latest and greatest version of python (3.6)")

version = __import__("analyticord").__version__

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(name="analyticord",
      version=version,
      description="Analyticord client for python.",
      url="https://github.com/analyticord/module-python",
      packages=find_packages(),
      install_requires=requirements)
