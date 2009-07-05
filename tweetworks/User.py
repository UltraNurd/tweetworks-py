# -*- coding: utf-8 -*-
"""
Read Tweetworks API users from XML responses.

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

class User:
    """
    Represents the data fields of a single Tweetworks user.
    """

    def __init__(self, xml = None):
        """
        Reads user fields from the XML, or create an empty user.

        id - int - Tweetworks numeric user ID
        username - string - Tweetworks/Twitter username
        avatar_url - string - Twitter avatar URL
        twitter_id - int - Twitter numeric user ID
        """

        # Initialize an empty user if no XML was provided
        if xml == None:
            self.id = None
            self.username = ""
            self.avatar_url = ""
            self.twitter_id = None
            return

        # User ID
        self.id = int(xml.xpath("/user/id/text()")[0])

        # User's Twitter username
        self.username = unicode(xml.xpath("/user/username/text()")[0])

        # User avatar URL (loaded from Amazon S3, obtained from Twitter)
        self.avatar_url = unicode(xml.xpath("/user/avatar_url/text()")[0])

        # User's "real" name
        self.name = unicode(xml.xpath("/user/name/text()")[0])

        # Twitter ID of the user; this should always be present but isn't always
        twitter_id = xml.xpath("/user/twitter_id/text()")
        if len(twitter_id) == 1:
            self.twitter_id = int(twitter_id[0])
        else:
            self.twitter_id = None

    def __str__(self):
        """
        Returns this User as an XML string.
        """
        
        # Get the XML tree and stringify
        return lxml.etree.tostring(self.xml())

    def __repr__(self):
        """
        Returns an eval-ready string for this User's constructor.
        """

        return "tweetworks.User(lxml.etree.parsestring(%s))" % repr(str(self))

    def xml(self):
        """
        Generates an XML element tree for this User.
        """

        # Construct the XML tree representing this User
        xml = E("user",
                E("id", str(self.id)),
                E("username", self.username),
                E("avatar_url", self.avatar_url),
                E("name", self.name),
                E("twitter_id",
                  ("", str(self.twitter_id))[self.twitter_id != None]),
                )
        
        # Return the XML tree (NOT a string)
        return xml
