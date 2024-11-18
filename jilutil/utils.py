from datetime import datetime
import os

def format(jobs, file):
    """Writes jobs back to .JIL format"""

    with open(file, 'w') as f:
        for job in jobs:
            f.write(str(job) + '\n')