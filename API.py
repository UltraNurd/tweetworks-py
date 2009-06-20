"""
Generate Tweetworks API requests and handle the response.

Nicolas Ward
@ultranurd
2009.06.19
"""

# System includes
import sys
import os
import urllib
import urllib2
import lxml.etree

# Tweetworks includes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import Post

class API:
    """
    Implement the Tweetworks API with HTTP POSTs.
    """

    class TweetworksException(Exception):
        """
        Errors in handling Tweetworks API calls.
        """

        def __init__(self, value):
            self.parameter = value
        def __str__(self):
            return repr(self.parameter)

    def __init__(self, api_key):
        """
        We need a Tweetworks API key to send requests.
        """

        self.api_key = api_key

    def request(self, url, data = {}):
        """
        POST the data (if any) to the specified URL, and return the parsed
        XML. An exception is thrown if there was an error.
        """

        # Add the API key and encode the data
        data["data[key]"] = self.api_key
        encoded_data = urllib.urlencode(data)

        # Construct the request and read the response
        request = urllib2.Request(url, encoded_data)
        response = urllib2.urlopen(request)

        # Parse the XML response
        xml_response = lxml.etree.parse(response)
        print lxml.etree.tostring(xml_response, pretty_print=True)
        
        # Check for errors
        error = xml_response.xpath("/error/text/text()")
        if len(error) > 0:
            raise API.TweetworksException(error[0])

        # Return the response XML
        return xml_response

    def read_post_xml(self, posts_xml):
        """
        Converts a <posts> element to a list of Post objects.
        """

        # Loop over the <post> elements
        posts = []
        for post_xml in posts_xml.xpath("/posts/post"):
            post_string = lxml.etree.tostring(post_xml)
            posts.append(Post.Post(lxml.etree.fromstring(post_string)))

        # Return the read posts
        return posts

    def view_posts(self, id):
        """
        Retrieves a single discussion and threaded list of replies.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/view/%d.xml" % id

        # Read the posts from the response XML
        return self.read_post_xml(self.request(url))
