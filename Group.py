"""
Read Tweetworks API groups from XML responses.

Nicolas Ward
@ultranurd
2009.06.19
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
        self.name = str(xml.xpath("/group/name/text()")[0])

        # Whether or not this group is private
        private = xml.xpath("/group/private/text()")
        if len(private) == 1 and private[0] == "1":
            self.private = True
        else:
            self.private = False

        # Prose description of the group
        description = xml.xpath("/group/description/text()")
        if len(description) == 1:
            self.description = str(description[0])
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

        return "Group(lxml.etree.parsestring(%s))" % repr(str(self))

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
