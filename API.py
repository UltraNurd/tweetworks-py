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
import Group
import User

class API:
    """
    Implement the Tweetworks API with HTTP POSTs.

    In general, API methods are named for their URL, and are organized by type:
    post-, group-, and user-related methods.
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
            else:
                raise API.TweetworksException(str(e), url)

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

    def read_group_xml(self, groups_xml):
        """
        Converts a <groups> element to a list of Group objects.
        """

        # Loop over the <group> elements
        groups = []
        for group_xml in groups_xml.xpath("/groups/group"):
            group_string = lxml.etree.tostring(group_xml)
            groups.append(Group.Group(lxml.etree.fromstring(group_string)))

        # Return the read groups
        return groups

    def read_user_xml(self, users_xml):
        """
        Converts a <users> element to a list of User objects.
        """

        # Loop over the <user> elements
        users = []
        for user_xml in users_xml.xpath("/users/user"):
            user_string = lxml.etree.tostring(user_xml)
            users.append(User.User(lxml.etree.fromstring(user_string)))

        # Return the read users
        return users

    def add_posts(self, body, group_id = None, parent_id = None, tweet = False):
        """
        Submits a post with the specified body text as the authenticated user.
        The destination group ID is optional (if none, the post will be public);
        the parent ID is optional (if none, the post will be top-level);
        the post can be optionally sent to Twitter. If a parent ID is supplied
        for a group post, the group ID is not necessary.

        Requires authentication; post will originate from that user.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/add.xml"

        # Format the post data
        data = {"data[Post][body]" : body,
                "data[Post][groupId]" : ("", str(group_id))[group_id != None],
                "data[Post][parentId]" : ("", str(parent_id))[parent_id != None],
                "data[Post][sendToTwitter]" : (0, 1)[tweet]}

        # Read the post from the response XML
        return Post.Post(self.request(url, data))

    def contributed_posts(self, username, recent = False):
        """
        Retrieves all posts contributed by the specified user; optionally only
        recently updated posts. Posts are returned in descending order by date.

        Requires authentication from the specified user.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/contributed/%s/%s.xml" % (username, ("newest", "updated")[recent])

        # Read the posts from the response XML
        return self.read_post_xml(self.request(url))

    def group_posts(self, group, recent = False):
        """
        Retrieves all posts contained in the specified group; optionally only
        recently updated posts. Posts are returned in descending order by date.

        A private group requires authentication from a user in that group.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/group/%s/%s.xml" % (group, ("newest", "updated")[recent])

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

    def index_groups(self):
        """
        Retrieves the list of Tweetworks groups.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/index.xml"

        # Read the groups from the response XML
        return self.read_group_xml(self.request(url))

    def join_groups(self, group):
        """
        Retrieves the list of Tweetworks groups.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/join/%s.xml" % group

        # Read the groups from the response XML
        groups = self.read_group_xml(self.request(url))
        if len(groups) == 1:
            # Return the joined group
            return groups[0]
        else:
            # Something weird happened to result in non-unary group result
            raise API.TweetworksException("%d groups were joined" % len(posts),
                                          url)

    def joined_groups(self, username):
        """
        Retrieves all groups of which the specified user is a member.

        Requires authentication from the specified user.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/joined/%s.xml" % username

        # Read the groups from the response XML
        return self.read_group_xml(self.request(url))

    def search_groups(self, query):
        """
        Searches groups for the specified query string, including name,
        description, and posts.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/search.xml"

        # Format the post data
        data = {"data[query]" : query}

        # Read the groups from the response XML
        return self.read_group_xml(self.request(url, data))

    def group_users(self, group):
        """
        Retrieves the list of users who are members of the specified group.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/users/group/%s.xml" % group

        # Read the users from the response XML
        return self.read_user_xml(self.request(url))

    def index_users(self):
        """
        Retrieves the list of Tweetworks users.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/users/index.xml"

        # Read the users from the response XML
        return self.read_user_xml(self.request(url))

    def search_users(self, query):
        """
        Searches usernames and real names for the specified query string..
        """

        # Format the request URL
        url = "http://www.tweetworks.com/users/search.xml"

        # Format the post data
        data = {"data[query]" : query}

        # Read the users from the response XML
        return self.read_user_xml(self.request(url, data))
