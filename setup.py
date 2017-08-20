import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    raise RuntimeError("analyticord requires a newer version of python (3.5)")

version = __import__("analyticord").__version__

with open("requirements.txt") as f:
    requirements = f.readlines()

setup(name="analyticord",
      version=version,
      description="Analyticord client for python.",
      url="https://github.com/analyticord/module-python",
      packages=find_packages(),
      install_requires=requirements,
      extras_require={
          "docs": [
              "sphinx-autodoc-typehints >= 1.2.1",
              "sphinxcontrib-asyncio"
          ]
      })
