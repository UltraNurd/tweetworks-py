# -*- coding: utf-8 -*-
"""
Read Tweetworks API groups from XML responses.

Nicolas Ward
@ultranurd
ultranurd@yahoo.com
http://www.ultranurd.net/code/tweetworks/
2009.06.19
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
import lxml.etree
from lxml.builder import E

class Group:
    """
    Represents the data fields of a single Tweetworks group.
    """

    def __init__(self, xml = None):
        """
        Reads group fields from the XML, or create an empty group.

        id - int - Tweetworks numeric group ID
        name - string - Tweetworks group name
        private - boolean - Whether or not this is a private group
        description - string - The short group description, if any
        """

        # Initialize an empty group if no XML was provided
        if xml == None:
            self.id = None
            self.name = ""
            self.private = False
            self.description = ""
            return

        # Group ID
        self.id = int(xml.xpath("/group/id/text()")[0])

        # Group name
        self.name = unicode(xml.xpath("/group/name/text()")[0])

        # Whether or not this group is private
        private = xml.xpath("/group/private/text()")
        if len(private) == 1 and private[0] == "1":
            self.private = True
        else:
            self.private = False

        # Prose description of the group
        description = xml.xpath("/group/description/text()")
        if len(description) == 1:
            self.description = unicode(description[0])
        else:
            self.description = ""

    def __str__(self):
        """
        Returns this Group as an XML string.
        """
        
        # Get the XML tree and stringify
        return lxml.etree.tostring(self.xml())

    def __repr__(self):
        """
        Returns an eval-ready string for this Group's constructor.
        """

        return "tweetworks.Group(lxml.etree.parsestring(%s))" % repr(str(self))

    def xml(self):
        """
        Generates an XML element tree for this Group.
        """

        # Construct the XML tree representing this Group
        xml = E("group",
                E("id", str(self.id)),
                E("name", self.name),
                (E("private"), E("private", "1"))[self.private]
                )

        # Add the group description, if there is one
        if self.description != "":
            xml.append(E("description", self.description))
        
        # Return the XML tree (NOT a string)
        return xml
