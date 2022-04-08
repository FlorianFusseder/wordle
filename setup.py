from setuptools import setup

setup(
    name="wordle_helper",
    version='0.1',
    py_modules=['wordle_helper'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        wordle=wordle:wordle
        wt=word_list:cli
        bot=bot:cli
    ''',
)
