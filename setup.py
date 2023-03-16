from distutils.core import setup

setup(
    name='aiven_metadata_parser',
    packages=['aiven_metadata_parser'],
    version='1.0.0',
    license='apache-2.0',
    description=' A python tool scraping Aiven services metadata and building a connected graph.',
    author='Open Source @ Aiven',
    url='https://github.com/aiven/metadata-parser',

    download_url='TBD',
    keywords=['kafka', 'faker', 'producer'],
    install_requires=[
        'psycopg2-binary',
        'requests',
        'simplejson',
        'aiven.client',
        'configparser',
        'pyvis==0.3.1',
        'networkx=2.8.8',
        'dash',
        'plotly',
        'pymysql',
        'pydot',
        'colour',
        'cryptography',
        'sqllineage',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache license 2.0',
        'Programming Language :: Python :: 3.7',
    ],
)
