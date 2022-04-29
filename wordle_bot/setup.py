from setuptools import setup

setup(
    name="wordle_bot",
    version='0.1',
    py_modules=['wordle_bot'],
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
