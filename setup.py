# -*- coding: utf-8 -*-

from setuptools import (
    find_packages,
    setup,
)

extras = {}
extras['test'] = [
    'pytest>=5.2.0,<6',
    'pytest-cov>=2.8.1,<3',
    'coveralls[yaml]>=1.8.2,<2',
    'pytest-xdist>=1.30.0,<2',
    'eth-tester[py-evm]>=0.3.0b1,<0.4',
    'web3>=5.2.0,<5.3.0',
    'tox>=3.7,<4',
    'hypothesis[lark]>=4.53.2,<5',
]
extras['lint'] = [
    'flake8>=3.7,<4',
    'flake8-bugbear>=19.8.0,<20',
    'flake8-use-fstring>=1.0.0,<2.0.0',
    'isort>=4.2.15,<5',
    'mypy>=0.740,<1',
]
extras['dev'] = extras['test'] + extras['lint'] + [
    'ipython',
]


setup(
    name='vyper',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='0.1.0-beta.16',
    description='Vyper: the Pythonic Programming Language for the EVM',
    author='Vyper Team',
    author_email='',
    url='https://github.com/vyperlang/vyper',
    license="MIT",
    keywords='ethereum evm smart contract language',
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3.6',
    py_modules=['vyper'],
    install_requires=[
        'lark-parser>=0.7.8,<1',
    ],
    setup_requires=[
        'pytest-runner',
        'setuptools-markdown'
    ],
    tests_require=extras['test'],
    extras_require=extras,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache 2.0 License',
        'Programming Language :: Python :: 3.8',
    ],
)
