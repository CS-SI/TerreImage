class TerreImageParamaters(object):
    """
    """
    instance = None
    def __new__(cls, *args, **kwargs): # __new__ always a classmethod
        if not cls.instance:
            cls.instance = super(TerreImageParamaters, cls).__new__(cls, *args, **kwargs)
            cls.instance.__private_init__()
        return cls.instance
    
    def __private_init__(self):
        """
        Init to have constant values
        """
        self.red_min = None
        self.red_max = None
        self.green_min = None
        self.green_max = None
        self.blue_min = None
        self.blue_max = None
        
    def is_complete(self):
        return self.red_max and self.red_min and self.blue_max and self.blue_min and self.green_max and self.green_min