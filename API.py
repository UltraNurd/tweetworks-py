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

    In general, API methods are named for their URL.
    """

    class TweetworksException(Exception):
        """
        Errors in handling Tweetworks API calls.
        """

        def __init__(self, value, url = ""):
            # Store the URL that caused the error
            self.url = url

            # Combine the URL with the error message
            if url != "":
                self.parameter = "%s: %s" % (url, value)
            else:
                self.parameter = value

        def __str__(self):
            return repr(self.parameter)

    def __init__(self, api_key, username = "", password = ""):
        """
        We need a Tweetworks API key to send requests. Optionally specify a
        Tweetworks username and password to use those methods that require
        authentication.
        """

        # Store the developer's API that will be used to make requests
        self.api_key = api_key

        # If a username and password were specified, set up authentication
        if username != "" and password != "":
            password_mgr = urllib2.HTTPPasswordMgr()
            password_mgr.add_password("Login please",
                                      "http://www.tweetworks.com",
                                      username, password)
            auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
            self.auth = urllib2.build_opener(auth_handler)
        else:
            self.auth = None

    def request(self, url, data = {}):
        """
        POST the data (if any) to the specified URL, and return the parsed
        XML. An exception is thrown if there was an error.
        """

        # Add the API key and encode the data
        data["data[key]"] = self.api_key
        encoded_data = urllib.urlencode(data)

        # Construct the request
        request = urllib2.Request(url, encoded_data)

        # Check for HTTP request errors
        try:
            # Use an authenticating URL opener if necessary
            if self.auth != None:
                response = self.auth.open(request)
            else:
                response = urllib2.urlopen(request)
        except urllib2.HTTPError, e:
            # Authentication error
            if e.code == 401:
                raise API.TweetworksException("Authentication required", url)

        # Parse the XML response
        xml_response = lxml.etree.parse(response)
        print lxml.etree.tostring(xml_response, pretty_print=True)
        
        # Check for errors
        error = xml_response.xpath("/error/text/text()")
        if len(error) > 0:
            raise API.TweetworksException(error[0], url)

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

    def contributed_posts(self, username, recent = False):
        """
        Retrieves all posts contributed by the specified user; optionally only
        recently updated posts. Posts are returned in descending order by date.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/contributed/%s/%s.xml" % (username, ("newest", "updated")[recent])

        # Read the posts from the response XML
        return self.read_post_xml(self.request(url))

    def view_posts(self, id):
        """
        Retrieves a single discussion and threaded list of replies.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/view/%d.xml" % id

        # Read the posts from the response XML
        posts = self.read_post_xml(self.request(url))
        if len(posts) == 1:
            # Return the single post
            return posts[0]
        else:
            # Something weird happened to result in non-unary post result
            raise API.TweetworksException("%d posts were returned" % len(posts),
                                          url)
