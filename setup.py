from setuptools import setup, find_packages
setup(
    name = 'share.kirschbaum.cloud.cli',
    version = '0.0.1',
    author = 'Lars Kirschbaum',
    author_email = 'lars@kirschbaum.me',
    url = '<github url where the tool code will remain>',
    py_modules = ['share'],
    packages = find_packages(),
    install_requires = ["Authlib", "requests_oauth2client"],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points = '''
        [console_scripts]
    '''
)
