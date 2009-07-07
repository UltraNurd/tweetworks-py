# -*- coding: utf-8 -*-
"""
Define setuptools options for the Python Tweetworks API.

Nicolas Ward
@ultranurd
ultranurd@yahoo.com
http://www.ultranurd.net/code/tweetworks/
2009.07.04
"""

"""
This file is part of the Tweetworks Python API.

Copyright © 2009 Nicolas Ward

Tweetworks Python API is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Tweetworks Python API is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with the Tweetworks Python API. If not, see http://www.gnu.org/licenses/

The term "Tweetworks" is Copyright © 2009 Tweetworks, LLC and is used
under license. See http://www.tweetworks.com/pages/terms

The use of this software requires a unique Tweetworks API key. You must be a
registered Tweetworks user, and have received an API key after requesting one
via http://www.tweetworks.com/pages/contact.

The term "Twitter" is Copyright © 2009 Twitter, Inc.
"""

# System includes
from setuptools import setup, find_packages

# Define the package
setup(
    # Package definition
    name = "tweetworks",
    version = "1.0.0b1",
    packages = find_packages(),
    include_package_data = True,
    exclude_package_data = {
        "":["LICENSE.txt", "README.txt", ".gitignore"]
        },

    # Dependencies
    install_requires = [
        "lxml>=2.2",
        "iso8601>=0.1.4",
        ],
    setup_requires = [
        "setuptools",
        "setuptools-git>=0.3",
        ],

    # Metadata
    author = "Nicolas Ward",
    author_email = "ultranurd@yahoo.com",
    description = "Python bindings for the tweetworks.com web service API",
    long_description = open("README.txt").read(),
    license = "GPL",
    url = "http://www.ultranurd.net/code/tweetworks/",
)
