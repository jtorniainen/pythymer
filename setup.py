from setuptools import setup

setup(name='pythymer',
      version='0.0.1',
      description='A handler for thyme (written in Python3!)',
      author='jtorniainen',
      url='https://github.com/jtorniainen/pythymer',
      license='MIT',
      packages=['pythymer'],
      package_dir={'pythymer': 'pythymer'},
      include_package_data=False,
      entry_points={"console_scripts":
                    ["thymer = pythymer.pythymer:start_pythymer"]})
