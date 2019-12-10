from setuptools import setup, find_packages
setup(
    name='LifelinesTransform',
    version='0.1',
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'minio', 'molgenis-commander'],
    author='Fleur Kelpin',
    license='GNU Lesser General Public License 3.0',
    test_suite='nose.collector',
    tests_require=['nose', 'parameterized']
)