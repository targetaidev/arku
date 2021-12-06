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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
    ],
    python_requires='>=3.6',
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
        'click>=6.7',
        'pydantic>=1',
        'dataclasses>=0.6;python_version == "3.6"',
        'typing-extensions>=3.7;python_version < "3.8"'
    ],
    extras_require={
        'watch': ['watchgod>=0.4'],
    },
    setup_requires=[
        'setuptools_scm==3.3.3',
    ],
)
