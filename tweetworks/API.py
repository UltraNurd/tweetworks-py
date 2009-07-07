# -*- coding: utf-8 -*-
"""
Generate Tweetworks API requests and handle the response.

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
import sys
import os
import urllib
import urllib2
import lxml.etree

# Tweetworks includes
import tweetworks

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

    def __request(self, url, data = {}):
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
        #print url
        #print lxml.etree.tostring(xml_response, pretty_print=True)
        
        # Check for errors
        error = xml_response.xpath("/error/text/text()")
        if len(error) > 0:
            raise API.TweetworksException(error[0], url)

        # Return the response XML
        return xml_response

    def __request_all_pages(self, url, page_reader, data = {}):
        """
        Repeatedly requests the specified URL with the specified POST data,
        incrementing the page by 1 until no new pages are available. Each page
        is read by the specified reader to convert XML into a list of objects,
        which are appended. The final output list is returned.

        url must be specified ending in ? or & as appropriate for the query.
        """

        # Loop over the requested pages
        items = []
        page = 1
        last_items_xml_string = ""
        while True:
            # Add the current page number to the URL
            paged_url = "%spage=%d" % (url, page)
            
            # Read the items from the response XML
            items_xml = self.__request(paged_url, data)
            items_xml_string = lxml.etree.tostring(items_xml)

            # Check if this is the last page
            if (last_items_xml_string == items_xml_string):
                break

            # Append these new items to the list
            items = items + page_reader(items_xml)
            last_items_xml_string = items_xml_string

            # Increment the page
            page = page + 1

        # Return the full list of requested items
        return items

    def __read_post_xml(self, posts_xml):
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

    def __paginate_posts(self, url_prefix, sort_by_updated = False, pages = None, all = False, before_id = None, after_id = None):
        """
        Retrieves posts at the specified URL, paginating if necessary according
        to the options.

        sort_by_updated - Whether posts should be sorted in descending creation
                          order or by descending last updated order.

        pages - An optional list of specific pages to retrieve.
        all - Whether all posts at this URL should be retrieved.

        before_id - Retrieve posts created/updated before the specified post
        after_id - Retrieve posts created/updated after the specified post

        If no paging options are specified, 20 posts matching the criteria are
        retrieved.
        """

        # Format the request URL
        url = "%s/%s.xml" % (url_prefix, ("newest", "updated")[sort_by_updated])

        # Was a post offset specified?
        if before_id != None:
            # Format the post offset
            url += "?beforeId=%d" % before_id
            if after_id != None:
                url += "&afterId=%d" % after_id
        else:
            # Format the post offset
            if after_id != None:
                url += "?afterId=%d" % after_id

        # Are we retrieving a single page?
        if pages != None:
            # Don't allow all + page
            if all:
                raise API.TweetworksException("Conflicting pages requested")

            # Loop over the requested pages
            posts = []
            for page in pages:
                # Format the request URL
                if before_id != None or after_id != None:
                    page_url = "%s&page=%d" % (url, page)
                else:
                    page_url = "%s?page=%d" % (url, page)

                # Read the posts from the response XML
                posts = posts + self.__read_post_xml(self.__request(page_url))

            # Return the requested posts
            return posts
        else:
            # Are we retrieving all pages?
            if all:
                # Request the paginated posts as a single list
                return self.__request_all_pages(url + "&", self.__read_post_xml)
            else:
                # Read the posts from the response XML
                return self.__read_post_xml(self.__request(url))

    def __read_group_xml(self, groups_xml):
        """
        Converts a <groups> element to a list of Group objects.
        """

        # Loop over the <group> elements
        groups = []
        for group_xml in groups_xml.xpath("/groups/group"):
            group_string = lxml.etree.tostring(group_xml)
            groups.append(tweetworks.Group(lxml.etree.fromstring(group_string)))

        # Return the read groups
        return groups

    def __paginate_groups(self, url, data = {}, pages = None, all = False):
        """
        Retrieves groups at the specified URL, paginating if necessary according
        to the options.

        data - Any additional data to add to the request.

        pages - An optional list of specific pages to retrieve.
        all - Whether all posts at this URL should be retrieved.

        If no paging options are specified, 30 groups matching the criteria are
        retrieved.
        """

        # Are we retrieving a single page?
        if pages != None:
            # Don't allow all + page
            if all:
                raise API.TweetworksException("Conflicting pages requested")

            # Loop over the requested pages
            groups = []
            for page in pages:
                # Format the request URL
                page_url = "%s?page=%d" % (url, page)

                # Read the groups from the response XML
                groups = groups + self.__read_group_xml(self.__request(page_url, data))

            # Return the requested groups
            return groups
        else:
            # Are we retrieving all pages?
            if all:
                # Request the paginated groups as a single list
                return self.__request_all_pages(url + "?", self.__read_group_xml, data)
            else:
                # Read the groups from the response XML
                return self.__read_group_xml(self.__request(url, data))

    def __read_user_xml(self, users_xml):
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

    def __paginate_users(self, url, data = {}, pages = None, all = False):
        """
        Retrieves users at the specified URL, paginating if necessary according
        to the options.

        data - Any additional data to add to the request.

        pages - An optional list of specific pages to retrieve.
        all - Whether all posts at this URL should be retrieved.

        If no paging options are specified, 30 users matching the criteria are
        retrieved.
        """

        # Are we retrieving a single page?
        if pages != None:
            # Don't allow all + page
            if all:
                raise API.TweetworksException("Conflicting pages requested")

            # Loop over the requested pages
            users = []
            for page in pages:
                # Format the request URL
                page_url = "%s?page=%d" % (url, page)

                # Read the users from the response XML
                users = users + self.__read_user_xml(self.__request(page_url, data))

            # Return the requested users
            return users
        else:
            # Are we retrieving all pages?
            if all:
                # Request the paginated users as a single list
                return self.__request_all_pages(url + "?", self.__read_user_xml, data)
            else:
                # Read the users from the response XML
                return self.__read_user_xml(self.__request(url, data))

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
        return Post.Post(self.__request(url, data))

    def contributed_posts(self, username, sort_by_updated = False, pages = None, all = False, before_id = None, after_id = None):
        """
        Retrieves posts contributed by the specified user, selected by the
        specified optional criteria.

        Requires authentication from the specified user.
        """

        # Format the request URL prefix
        url_prefix = "http://www.tweetworks.com/posts/contributed/%s" % username

        # Return the read (and paginated) posts
        return self.__paginate_posts(url_prefix, sort_by_updated, pages, all, before_id, after_id)

    def group_posts(self, group, sort_by_updated = False, pages = None, all = False, before_id = None, after_id = None):
        """
        Retrieves posts contained in the specified group, selected by the
        specified optional criteria.

        A private group requires authentication from a user in that group.
        """

        # Format the request URL prefix
        url_prefix = "http://www.tweetworks.com/posts/group/%s" % group

        # Return the read (and paginated) posts
        return self.__paginate_posts(url_prefix, sort_by_updated, pages, all, before_id, after_id)

    def index_posts(self, sort_by_updated = False, pages = None, all = False, before_id = None, after_id = None):
        """
        Retrieves all posts, selected by the specified optional criteria.
        """

        # Format the request URL prefix
        url_prefix = "http://www.tweetworks.com/posts/index"

        # Return the read (and paginated) posts
        return self.__paginate_posts(url_prefix, sort_by_updated, pages, all, before_id, after_id)

    def joined_groups_posts(self, username, sort_by_updated = False, pages = None, all = False, before_id = None, after_id = None):
        """
        Retrieves posts contained in all of the groups joined by the specified
        user, selected by the specified optional criteria.

        Requires authentication from the specified user.
        """

        # Format the request URL prefix
        url_prefix = "http://www.tweetworks.com/posts/joined_groups/%s" % username

        # Return the read (and paginated) posts
        return self.__paginate_posts(url_prefix, sort_by_updated, pages, all, before_id, after_id)

    def view_posts(self, id):
        """
        Retrieves a single discussion and threaded list of replies.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/posts/view/%d.xml" % id

        # Read the posts from the response XML
        posts = self.__read_post_xml(self.__request(url))
        if len(posts) == 1:
            # Return the single post
            return posts[0]
        else:
            # Something weird happened to result in non-unary post result
            raise API.TweetworksException("%d posts were returned" % len(posts),
                                          url)

    def index_groups(self, pages = None, all = False):
        """
        Retrieves all Tweetworks groups, selected by the specified optional
        criteria.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/index.xml"

        # Return the read (and paginated) groups
        return self.__paginate_groups(url, {}, pages, all)

    def join_groups(self, group):
        """
        Join the specified Tweetworks group as the authenticated user.

        Requires authentication; the authenticated user will join the group.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/join/%s.xml" % group

        # Read the groups from the response XML
        groups = self.__read_group_xml(self.__request(url))
        if len(groups) == 1:
            # Return the joined group
            return groups[0]
        else:
            # Something weird happened to result in non-unary group result
            raise API.TweetworksException("%d groups were joined" % len(posts),
                                          url)

    def joined_groups(self, username, pages = None, all = False):
        """
        Retrieves all groups of which the specified user is a member, selected
        by the specified optional criteria.

        Requires authentication from the specified user.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/joined/%s.xml" % username

        # Return the read (and paginated) groups
        return self.__paginate_groups(url, {}, pages, all)

    def search_groups(self, query):
        """
        Searches groups for the specified query string, including name,
        description, and posts. Always returns all matches.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/groups/search.xml"

        # Format the post data
        data = {"data[query]" : query}

        # Return the read (and paginated) groups
        return self.__paginate_groups(url, data, all = True)

    def group_users(self, group, pages = None, all = False):
        """
        Retrieves all users who are members of the specified group, selected
        by the specified optional criteria.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/users/group/%s.xml" % group

        # Return the read (and paginated) users
        return self.__paginate_users(url, {}, pages, all)

    def index_users(self, pages = None, all = False):
        """
        Retrieves all Tweetworks users, selected by the specified optional
        criteria.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/users/index.xml"

        # Return the read (and paginated) users
        return self.__paginate_users(url, {}, pages, all)

    def search_users(self, query):
        """
        Searches usernames and real names for the specified query string. Always
        returns all matches.
        """

        # Format the request URL
        url = "http://www.tweetworks.com/users/search.xml"

        # Format the post data
        data = {"data[query]" : query}

        # Return the read (and paginated) users
        return self.__paginate_users(url, data, all = True)
