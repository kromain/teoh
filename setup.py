import sys
from setuptools import setup

package_platforms = ['win']
if sys.platform == 'win32':
    print("[NOTE] Linux/Mac package creation unsupported on Windows, only win32 package will be created.")
else:
    package_platforms.append('unix')


def setup_platform(package_platform):
    cmd_args = sys.argv[1:]
    if len(cmd_args) == 0:
        cmd_args.append("sdist")

    if package_platform == 'win':
        bin_dir = ['bin/win32/*']
        cmd_args.append("--formats=zip")
    else:
        bin_dir = ['bin/linux/*', 'bin/darwin/*']
        cmd_args.append("--formats=gztar")

    setup(
        name='skynet',
        version='0.1b1',
        description='The PlayStation Remote Control',
        author='Romain Pokrzywka',
        author_email='Romain.Pokrzywka@am.sony.com',
        license='LICENSE.txt',
        url='https://qmjira.snei.sony.com/confluence/pages/viewpage.action?title=Skynet+Home&spaceKey=SKYN',

        packages=[
            'skynet',
            'skynet.deci',
            'skynet.osk',
            'skynet.psdriver',
        ],

        package_data={
            # Also package and distribute the psdriver executables in skynet/psdriver/bin/<platform>
            'skynet.psdriver': bin_dir,
        },

        install_requires=[
            "selenium >= 2.42.1",
            "pytest >= 2.5.2",
        ],

        script_args=cmd_args
    )


for p in package_platforms:
    setup_platform(p)
