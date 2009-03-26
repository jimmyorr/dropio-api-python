class Resource(object):
    def __init__(self):
        pass


class Drop(Resource):
    def __init__(self, url, id):
        Resource.__init__(self)
        self.url = url
        self.id = id
    
    def __str__(self):
        return self.url


class Asset(Resource):
    """ 
    Based on http://groups.google.com/group/dropio-api/web/resource-descriptions
    (wrong)
    """
    def __init__(self, name, type, title, description, filesize, created_at,
                 thumbnail=None, status=None, file=None, converted=None, 
                 hidden_url=None, pages=None, duration=None, artist=None, 
                 track_title=None, height=None, width=None, contents=None, 
                 url=None):
        Resource.__init__(self)
        self.name = name
        self.type = type
        self.title = title
        self.description = description
        self.filesize = filesize
        self.created_at = created_at
    
    def __str__(self):
        return self.title
