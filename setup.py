from setuptools import setup, find_packages

setup(
    name='flvrbot',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.9.3',
        'aiosignal==1.3.1',
        'async-timeout==4.0.3',
        'asyncio==3.4.3',
        'attrs==23.2.0',
        'certifi==2024.2.2',
        'chardet==5.2.0',
        'charset-normalizer==3.3.2',
        'frozenlist==1.4.1',
        'greenlet==3.0.3',
        'idna==3.6',
        'lenny==0.1.3',
        'multidict==6.0.5',
        'psycopg2-binary==2.9.9',
        'py-cord==2.5.0',
        'pytz==2024.1',
        'requests==2.31.0',
        'SQLAlchemy==2.0.29',
        'typing_extensions==4.10.0',
        'urllib3==2.2.1',
        'websockets==12.0',
        'yarl==1.9.4',
        'pint==0.23',
        'python-dotenv==1.0.1'
    ],
)

