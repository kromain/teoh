#!/usr/bin/env python3
#
# Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.

import setuptools
import shutil
import subprocess
import sys


def setup_platform(package_platform, cmd_args):
    if len(cmd_args) == 0:
        cmd_args.append("sdist")

    if package_platform == 'win':
        bin_dir = ['bin/win32/*']
        cmd_args.append("--formats=zip")
    else:
        bin_dir = ['bin/linux/*', 'bin/darwin/*']
        cmd_args.append("--formats=gztar")

    do_setup(cmd_args, bin_dir)

    # setuptools doesn't clean up skynet.egg-info which interferes with subsequent calls to setup(), so do it manually
    shutil.rmtree("skynet.egg-info")


def do_setup(cmd_args, bin_dir):
    setuptools.setup(

        name='skynet',
        version='0.2b1',
        description='The PlayStation Remote Control',
        author='Romain Pokrzywka',
        author_email='Romain.Pokrzywka@am.sony.com',
        license='LICENSE.txt',
        url='https://qmjira.snei.sony.com/confluence/pages/viewpage.action?title=Skynet+Home&spaceKey=SKYN',

        packages=[
            'mantis',
            'skynet',
            'skynet.config',
            'skynet.deci',
            'skynet.osk',
            'skynet.psdriver',
        ],

        package_data={
            # Also package and distribute the psdriver executables in skynet/psdriver/bin/<platform>
            'skynet.psdriver': bin_dir,
        },

        entry_points={
            'console_scripts': [
                'mantis_run = mantis:testrunner_main',
                'skynet_run = mantis:testrunner_main',
                'ill_be_back = mantis:testrunner_main',
                'hasta_la_vista_baby = mantis:testrunner_main',
            ],
        },

        install_requires=[
            "selenium >= 2.43.0",
            "pytest >= 2.6.3",
            "pytest-xdist >= 1.11",
            "Pillow >= 2.6.0",
        ],

        script_args=cmd_args
    )


package_platforms = ['win', 'unix']

"""
We have to create each package using a new interpreter instance due to setuptools only allowing one setup at a time.
For that we do a recursive call to our script, passing the desired package platform as an extra cmdline argument.
If we don't detect the platform as the last argument, we are in the initial process, from which we spawn a new
subprocess for each package we need to generate.
If we detect the platform as the last argument, we proceed with the setuptools setup() call to create the package
using custom settings for that platform.
"""
if __name__ == '__main__':

    if sys.argv[-1] in package_platforms:
        # subprocess mode
        setup_platform(sys.argv[-1], sys.argv[1:-1])
    else:
        # initial process mode
        if len(sys.argv) > 1 and sys.argv[-1] != "sdist":
            do_setup(sys.argv[1:], ["bin/*/*"])
            sys.exit(0)

        if sys.platform == 'win32':
            print("[NOTE] Linux/Mac package creation unsupported on Windows, only Windows package will be created.")
            package_platforms.remove('unix')

        for p in package_platforms:
            print("[INFO] Creating {} package...".format(p))

            pargs = [sys.executable]
            pargs.extend(sys.argv)
            pargs.append(p)
            subprocess.call(pargs)

        print("[INFO] Finished! Packages have been created in dist/")
