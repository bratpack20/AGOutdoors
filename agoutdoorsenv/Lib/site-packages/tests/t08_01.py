

class CMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
class C(metaclass=CMeta):
    pass