from enum import Enum

class JobStatus(str, Enum):
    """Enumeration of possible job statuses."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed" 