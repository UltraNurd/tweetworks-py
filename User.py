"""
Read Tweetworks API users from XML responses.

Nicolas Ward
@ultranurd
2009.06.19
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
        self.username = str(xml.xpath("/user/username/text()")[0])

        # User avatar URL (loaded from Amazon S3, obtained from Twitter)
        self.avatar_url = str(xml.xpath("/user/avatar_url/text()")[0])

        # User's "real" name
        self.name = str(xml.xpath("/user/name/text()")[0])

        # Twitter ID of the user
        self.twitter_id = int(xml.xpath("/user/twitter_id/text()")[0])

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

        return "User(lxml.etree.parsestring(%s))" % repr(str(self))

    def xml(self):
        """
        Generates an XML element tree for this Post.
        """

        # Construct the XML tree representing this Post
        xml = E("user",
                E("id", str(self.id)),
                E("username", self.username),
                E("avatar_url", self.avatar_url),
                E("name", self.name),
                E("twitter_id", str(self.twitter_id)),
                )
        
        # Return the XML tree (NOT a string)
        return xml
