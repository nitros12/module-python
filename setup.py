from setuptools import find_packages, setup

with open('analyticord/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

REQUIRES = ["aiohttp"]

setup(
    name='analyticord',
    version=version,
    description='',
    long_description=readme,
    author='Ben Simms',
    author_email='ben@bensimms.moe',
    maintainer='Ben Simms',
    maintainer_email='ben@bensimms.moe',
    url='https://github.com/nitros12/analyticord',
    license='MIT',

    keywords=[
        '',
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    install_requires=REQUIRES,
    #tests_require=['coverage', 'pytest'],
    extras_require={
        "docs": [
            "sphinx-autodoc-typehints >= 1.2.1",
            "sphinxcontrib-asyncio"
            ]},
    packages=find_packages(),
)
