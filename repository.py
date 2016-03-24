class Repository:
    def __init__(self, req):
        self.json = req.get_json()
