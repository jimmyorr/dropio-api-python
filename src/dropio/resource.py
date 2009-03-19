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
    def __init__(self, title):
        Resource.__init__(self)
        self.title = title
    
    def __str__(self):
        return self.title
