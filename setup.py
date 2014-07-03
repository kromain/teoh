from setuptools import setup

setup(
    name='skynet',
    version='0.1b1',
    description='The PlayStation Remote Control',
    author='Romain Pokrzywka',
    author_email='Romain.Pokrzywka@am.sony.com',
    license='LICENSE.txt',
    url='https://qmjira.snei.sony.com/confluence/pages/viewpage.action?title=Skynet+Home&spaceKey=SKYN',

    packages=['skynet', 'skynet.deci', 'skynet.psdriver'],
    package_data = {
        # Also package and distribute the psdriver executables in skynet/psdriver/bin
        'skynet.psdriver': ['bin/*'],
    },

    install_requires=[
        "selenium >= 2.42.1",
        "pytest >= 2.5.2",
    ],
)
