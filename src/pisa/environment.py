"""Record direct and transitive analysis dependencies without importing them.

The list matches the observed dependency closure pinned in requirements.txt.
It describes Python distributions, not binary wheels, operating-system libraries
or the optional PDF-review renderer.
"""
import importlib.metadata
import sys
from . import __version__


DISTRIBUTIONS=(
    'contourpy','cycler','et_xmlfile','fonttools','kiwisolver','matplotlib',
    'numpy','openpyxl','packaging','pandas','patsy','pillow','pyparsing',
    'pypdf','python-dateutil','pytz','PyYAML','scipy','six','statsmodels','tzdata',
)


def package_versions():
    versions={}
    for name in DISTRIBUTIONS:
        try:
            versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name]=None
    return versions


def runtime_identity():
    return {'project_version':__version__,'python':sys.version,'platform':sys.platform,
            'packages':package_versions()}
