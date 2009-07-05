# -*- coding: utf-8 -*-
"""
Read Tweetworks API posts from XML responses.

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
import iso8601
import lxml.etree
from lxml.builder import E

# Tweetworks includes
import tweetworks

class Post:
    """
    Represents the data fields of a single Tweetworks post.
    """

    def __init__(self, xml = None):
        """
        Reads post fields from the XML, or create an empty post.

        id - int - Tweetworks numeric post ID
        user_id - int - Tweetworks numeric user ID of poster
        group_id - int - Tweetworks numeric ID of containing group, if any
        parent_id - int - Tweetworks numeric ID of parent post, if any
        twitter_id - int - Twitter numeric ID of post, if cross-posted
        bingo - boolean - Whether this post has been marked as a bingo
        body - string - The contents of this post
        created - datetime - When this post was created on Tweetworks
        group - tweetworks.Group - Object representing containing group, if any
        user - tweetworks.User - Object representing poster
        replies - int - The number of replies to this post, if any
        posts - tweetworks.Post[] - The Post object replies to this post, if any
        """

        # Initialize an empty post if no XML was provided
        if xml == None:
            self.id = None
            self.user_id = None
            self.group_id = None
            self.parent_id = None
            self.twitter_id = None
            self.bingo = False
            self.body = ""
            self.created = datetime.datetime.now()
            self.group = None
            self.user = None
            self.replies = 0
            self.posts = []
            return

        # Post ID
        self.id = int(xml.xpath("/post/id/text()")[0])

        # Tweetworks User ID
        self.user_id = int(xml.xpath("/post/user_id/text()")[0])

        # Group ID, if the post wasn't public
        group_id = xml.xpath("/post/group_id/text()")
        if len(group_id) == 1:
            self.group_id = int(group_id[0])
        else:
            self.group_id = None

        # Parent ID, if the post was a reply
        parent_id = xml.xpath("/post/parent_id/text()")
        if len(parent_id) == 1:
            self.parent_id = int(parent_id[0])
        else:
            self.parent_id = None
        
        # Twitter ID of the post, if it was cross-posted
        twitter_id = xml.xpath("/post/twitter_id/text()")
        if len(twitter_id) == 1:
            self.twitter_id = int(twitter_id[0])
        else:
            self.twitter_id = None

        # Whether or not this post has been marked as a Bingo
        bingo = xml.xpath("/post/bingo/text()")
        if len(bingo) == 1 and bingo[0] == "1":
            self.bingo = True
        else:
            self.bingo = False

        # The text contents of the post
        self.body = unicode(xml.xpath("/post/body/text()")[0])

        # The timestamp of the post
        self.created = iso8601.parse_date(xml.xpath("/post/created/text()")[0])

        # The number of replies to this post, if any
        replies = xml.xpath("/post/replies/text()")
        if len(replies) == 1:
            self.replies = int(replies[0])
        else:
            self.replies = 0

        # Group metadata, if the post wasn't public
        if self.group_id != None:
            group_string = lxml.etree.tostring(xml.xpath("/post/group")[0])
            self.group = tweetworks.Group(lxml.etree.fromstring(group_string))
        else:
            self.group = None

        # Post author metadata
        user_string = lxml.etree.tostring(xml.xpath("/post/user")[0])
        self.user = tweetworks.User(lxml.etree.fromstring(user_string))

        # The replies to this post, if any (select only non-empty child posts)
        self.posts = []
        for post_xml in xml.xpath("/post/posts/post[node()]"):
            post_string = lxml.etree.tostring(post_xml)
            self.posts.append(Post(lxml.etree.fromstring(post_string)))

    def __str__(self):
        """
        Returns this Post as an XML string.
        """
        
        # Get the XML tree and stringify
        return lxml.etree.tostring(self.xml())

    def __repr__(self):
        """
        Returns an eval-ready string for this Post's constructor.
        """

        return "tweetworks.Post(lxml.etree.parsestring(%s))" % repr(str(self))

    def xml(self):
        """
        Generates an XML element tree for this Post.
        """

        # Construct the XML tree representing this Post
        xml = E("post",
                E("id", str(self.id)),
                E("user_id", str(self.user_id)),
                (E("group_id"), 
                 E("group_id",
                   str(self.group_id)))[self.group_id != None],
                (E("parent_id"), 
                 E("parent_id",
                   str(self.parent_id)))[self.parent_id != None],
                (E("twitter_id"), 
                 E("twitter_id",
                   str(self.twitter_id)))[self.twitter_id != None],
                (E("bingo"), E("bingo", "1"))[self.bingo],
                E("body", self.body),
                E("created", str(self.created).replace(" ", "T")),
                E("replies", str(self.replies)),
                )

        # Append the parent group, if any
        if self.group == None:
            xml.append(E("group", E("id"), E("name"), E("private")))
        else:
            xml.append(self.group.xml())

        # Append the author user
        if self.user == None:
            xml.append(E("user"))
        else:
            xml.append(self.user.xml())

        # Append reply posts, if any
        if len(self.posts) > 0:
            posts_xml = E("posts", *[post.xml() for post in self.posts])
            xml.append(posts_xml)
        else:
            xml.append(E("posts", E("post")))
        
        # Return the XML tree (NOT a string)
        return xml
