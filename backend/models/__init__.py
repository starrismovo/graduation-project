"""Models package"""
# Lazy import - avoid circular dependencies
def __getattr__(name):
    if name == "User":
        from .user import User
        return User
    elif name == "Job":
        from .job import Job
        return Job
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

