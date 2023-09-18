import setuptools


def _get_long_description():
    with open('README.md') as readme_file:
        return readme_file.read()


setuptools.setup(
    name='arku',
    use_scm_version=True,
    description='Fast job queuing and RPC in Python with asyncio and Redis',
    long_description=_get_long_description(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
    ],
    project_urls={
        'Documentation': 'https://arku.readthedocs.io',
        'Code': 'https://github.com/targetaidev/arku',
        'Issues': 'https://github.com/targetaidev/arku/issues',
    },
    python_requires='>=3.8,<4',
    author='TargetAI Ltd.',
    author_email='dev@targetai.kz',
    url='https://github.com/targetaidev/arku',
    license='MIT',
    packages=['arku'],
    package_data={'arku': ['py.typed']},
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'arku=arku.cli:cli',
        ],
    },
    install_requires=[
        'click>=6.7,<9',
        'redis>=4.2,<6',
    ],
    extras_require={
        'dev': [
            'flake8-quotes==3.3.2',
            'flake8==6.1.0',
            'isort==5.12.0',
            'msgpack==1.0.5',
            'watchgod>=0.8.2',
        ],
        'doc': [
            'docutils==0.14',
            'pygments==2.7.4',
            'sphinx==2.0.1',
            'sphinxcontrib-websupport==1.1.0',
        ],
        'test': [
            'coverage==7.3.1',
            'dirty-equals==0.6.0',
            'pytest-aiohttp==0.3.0',
            'pytest-cov==2.8.1',
            'pytest-mock==3',
            'pytest-sugar==0.9.2',
            'pytest-timeout==1.3.3',
            'pytest==5.3.5',
        ],
    },
    setup_requires=[
        'setuptools_scm==3.3.3',
    ],
)
