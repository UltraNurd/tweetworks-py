"""
Tweetworks Python modules.

Implements the Tweetworks API as Python objects and methods.

Nicolas Ward
@ultranurd
2009.06.19
"""

# Use system modules for directory manipulation
import os

# Generate a list of the modules in this directory
modules = []
for filename in os.listdir(__path__[0]):
	if filename[-3:] == '.py' and not filename == '__init__.py':
		modules.append(filename[:-3])

# Run the module import commands
for module in modules:
    exec 'import %s' % module
