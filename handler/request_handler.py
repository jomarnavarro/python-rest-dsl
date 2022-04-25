import requests
import json

class RequestHandler(object):
    """ Base URL Fragment which has knowledge about magical bits around it """
    requestMethods = ["GET", "POST", "DELETE", "PUT", "PATCH"]
    requestMapping = {}
    def __init__(self, fragments):
        self.fragments = fragments
    def __getattr__(self, name):
        """ Defer all the magic here: if we get a requestMethod, we return a
        function which can be invoked using the requests library, otherwise we
        build a map using the meta shit defined below"""
        if (name == "id"):
            # Prevent base nesting itself with ids
            if (self.__class__ == TypiBase):
                return self
            return IdFragment(self.fragments, self.__class__)
        elif (name in self.requestMethods):
            url = "/".join(self.fragments)
            print(url)
            return RequestWrapper(method=name, url=url)
        elif (name in self.requestMapping):
            # print "attempted request map %s" % (name)
            # TODO: add error handling here if requestMapping does not exist in name
            nextObj = self.requestMapping[name]
            new_fragments = list(self.fragments)
            new_fragments.append(nextObj.fragmentUrl)
            return nextObj(new_fragments)
        else:
            raise AttributeError("API has no subpath: %s. Allowed: %s" %
                                 (name, ",".join(self.requestMapping.keys())))
    def __str__(self):
        return "/".join(self.fragments)
    def __dir__(self):
        return sorted(set(
            dir(type(self)) + self.__dict__.keys() + self.requestMethods
            + self.requestMapping.keys()
        ))
    def __repr__(self):
        return "<" + str(self) + ">"

class RequestWrapper:
    """ Wraps up a Request object so that appending options has the same API """
    def __init__(self, method, url):
        headers = {"content-type": "application/json"}
        self.options = {"method": method, "url": url, "headers": headers}

    def __call__(self, **kwargs):
        """ Delegates work to the requests library below. Passes options to the requests library
        with the notable extras:
         - auth encodes with basic-auth. it will take either a tuple consisting of
           (username, password) or convert any dictionary with username and password fields set
        """

        options = {**self.options, **kwargs}
        print(options)
        # options = self.options.items().update(kwargs.items()) # dict(self.options.items() | kwargs.items())
        data = options.get("data")
        print(data)
        if (data is not None):
            content_type = options["headers"]["content-type"]
            if (content_type == "application/json"):
                options["data"] = json.dumps(data)
        r = requests.Request(**options).prepare()
        s = requests.Session()
        return s.send(r)

class IdFragment(RequestHandler):
    """ Returns an id handler which follows the mapping of the preceding API """
    def __init__(self, fragments, handlerClass):
        self.fragments = fragments
        self.handlerClass = handlerClass
    def __call__(self, value):
        """ Append this fragment to itself """
        new_fragments = list(self.fragments)
        new_fragments.append(str(value))
        return self.handlerClass(new_fragments)


class DomainId(RequestHandler):
    requestMethods = ["GET", "POST"]
    fragmentUrl = "domain_id"
class Comment(RequestHandler):
    fragmentUrl = "comments"
class Post(RequestHandler):
    fragmentUrl = "posts"
    requestMapping = {
        "domain_id": DomainId,
        "comments": Comment
    }

class Album(RequestHandler):
    fragmentUrl = "albums"
class Photo(RequestHandler):
    fragmentUrl = "photos"
class Todo(RequestHandler):
    fragmentUrl = "todos"
class User(RequestHandler):
    fragmentUrl = "users"
class TypiBase(RequestHandler):
    """ Base URL Fragment which has knowledge about the magical bits around it. """
    requestMethods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    requestMapping = {
        "posts": Post,
        "comments": Comment,
        "albums": Album,
        "photos": Photo,
        "todos": Todo,
        "users": User
    }
    def __init__(self, api_url):
        if isinstance(api_url, list):
            self.fragments = api_url
        else:
            self.fragments = [api_url]
        
        self.options = {}
    def __call__(self, *args):
        return self