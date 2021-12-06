import pathlib
import setuptools


description = 'Job queues in python with asyncio and redis'
readme = pathlib.Path(__file__).parent / 'README.md'
if readme.exists():
    long_description = readme.read_text()
else:
    long_description = description + '.\n\nSee https://arq-docs.helpmanual.io/ for documentation.'


setuptools.setup(
    name='arq',
    use_scm_version=True,
    description=description,
    long_description=long_description,
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
    python_requires='>=3.8',
    author='Samuel Colvin',
    author_email='s@muelcolvin.com',
    url='https://github.com/samuelcolvin/arq',
    license='MIT',
    packages=['arq'],
    package_data={'arq': ['py.typed']},
    zip_safe=True,
    entry_points="""
        [console_scripts]
        arq=arq.cli:cli
    """,
    install_requires=[
        'aioredis>=2.0,<3',
        'click>=6.7,<9',
        'pydantic>=1,<2',
    ],
    extras_require={
        'dev': [
            'black==21.12b0',
            'flake8-quotes==3',
            'flake8==3.7.9',
            'isort==5.8.0',
            'msgpack==0.6.1',
            'mypy==0.812',
            'pycodestyle==2.5.0',
            'pyflakes==2.1.1',
            'twine==3.1.1',
            'watchgod>=0.4',
        ],
        'doc': [
            'docutils==0.14',
            'pygments==2.7.4',
            'sphinx==2.0.1',
            'sphinxcontrib-websupport==1.1.0',
        ],
        'test': [
            'coverage==5.1',
            'pytest-aiohttp==0.3.0',
            'pytest-cov==2.8.1',
            'pytest-mock==3',
            'pytest-sugar==0.9.2',
            'pytest-timeout==1.3.3',
            'pytest-toolbox==0.4',
            'pytest==5.3.5',
        ],
    },
    setup_requires=[
        'setuptools_scm==3.3.3',
    ],
)
