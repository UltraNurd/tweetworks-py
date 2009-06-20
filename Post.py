"""
Read Tweetworks API posts from XML responses.

Nicolas Ward
@ultranurd
2009.06.19
"""

# System includes
import iso8601
import lxml.etree

class Post:
    """
    Represents the data fields of a single Tweetworks post.
    """

    def __init__(self, xml):
        """
        Reads post fields from the XML.
        """

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
            self.parent_id = int(parent_id)
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
        self.body = xml.xpath("/post/body/text()")[0]

        # The timestamp of the post
        self.created = iso8601.parse_date(xml.xpath("/post/created/text()")[0])

        # Group metadata, if the post wasn't public
        if self.group_id != None:
            self.group = None
            #self.group = Group.Group(xml.xpath("/post/group")[0])
        else:
            self.group = None

        # Post author metadata
        #self.user = User.User(xml.xpath("/post/user")[0])

        # The number of replies to this post, if any
        self.replies = int(xml.xpath("/post/replies/text()")[0])
