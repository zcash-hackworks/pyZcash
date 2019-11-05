from setuptools import setup

setup(name='pyZcash',
      version='0.1',
      description='Python wrapper for Zcash cli',
      url='https://github.com/zcash-hackworks/pyZcash',
      author='ECC sysadmin',
      author_email='sysadmin@electriccoin.co',
      license='MIT',
      packages=setuptools.find_packages(),
      python_requires='>=3.6',
      install_requires=[
          'requests',
      ])