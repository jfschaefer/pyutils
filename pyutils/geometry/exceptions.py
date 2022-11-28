

class ImmutableInstanceError(AttributeError):
    """ The object cannot be modified - you should probably create a new instance instead.
    Many objects in this library are immutable to enable hashing.
    """
    pass
