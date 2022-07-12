import os
import pkgutil
import doctest

import pyutils


def load_tests(loader, tests, ignore):
    for module_info in pkgutil.iter_modules(pyutils.__path__):
        if module_info.ispkg:
            path = os.path.join(pyutils.__path__[0], module_info.name)
            for m in pkgutil.iter_modules([path]):
                name = '.'.join([pyutils.__name__, module_info.name, m.name])
                if m.ispkg:
                    raise NotImplemented(f'Cannot import packages nested that deep: {name}')
                tests.addTests(doctest.DocTestSuite(name))
        else:
            tests.addTests(doctest.DocTestSuite(pyutils.__name__ + '.' + module_info.name))
    return tests
