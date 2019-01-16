import os

from setuptools import setup, find_packages


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*path.split('/'))
    return [req]


def _reqs(*f):
    return [
        _pip_requirement(r) for r in (
            strip_comments(l) for l in open(
            os.path.join(os.getcwd(), 'requirements', *f)).readlines()
        ) if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


setup(name='py-accengage',
      version='0.1',
      url='https://github.com/pualien/py-accengage',
      license='MIT',
      author='Matteo Senardi',
      author_email='pualien@gmail.com',
      description='Unofficcial library to connect to Accengage API',
      packages=find_packages(exclude=['tests']),
      install_requires=reqs('default.txt'),
      long_description=open('README.md').read(),
      zip_safe=False)
