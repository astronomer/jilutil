"""AutoSys JIL Utility (https://github.com/mscribellito/JIL-Utility)"""
import re
from collections import UserDict


class AutoSysJob(UserDict):
    r"""Regex pattern for matching job start comments
    >>> re.match(AutoSysJob.job_start_regex, 'insert_job: FOO\n\nbar: baz').group(1)
    'FOO'
    """

    """Class that represents a job within AutoSys and its attributes"""

    job_name_comment = '/* ----------------- {} ----------------- */'
    job_start_regex = '\\s*insert_job\\s*:\\s*([a-zA-Z0-9\\.\\#_-]{1,64})\\s*'


    def __init__(self, job_name = ''):
        """Instantiates a new instance"""

        super().__init__()
        self.job_name = job_name
        self.data['insert_job'] = job_name

    @property
    def attributes(self):
        """Returns attributes"""

        return self.data

    def __str__(self):
        """Returns string representation"""

        atts = self.data.copy()

        # insert special job name in comment format
        job_str = self.job_name_comment.format(atts['insert_job']) + '\n\n'

        # add special insert_job & job_type attributes
        job_str += 'insert_job: {}'.format(atts['insert_job'])
        del atts['insert_job']

        # iterate over attribute:value pairs in alphabetical order
        for attribute, value in sorted(atts.items()):
            if not value:
                continue
            # append att:val pair to job string
            job_str += '{}: {}\n'.format(attribute, value)

        return job_str

    @classmethod
    def from_str(cls, jil: str):
        """Creates a new job from a string"""

        job = cls()

        # force job_type onto a new line
        jil = jil.replace('job_type', '\njob_type', 1)
        jil = jil.replace('\r\n', '\n')

        # split lines and strip line if not empty
        lines = [line.strip() for line in jil.split('\n') if line.strip() != '']

        multiline_comment_mode = False
        for line in lines:
            # check if line is a comment
            if line.startswith('/*') or line.startswith('#'):
                multiline_comment_mode = line.startswith('/*') and '*/' not in line
                continue

            if multiline_comment_mode:
                multiline_comment_mode = '*/' not in line
                continue

            # remove inline comments at the end of the line
            line = re.sub(r"(/\*.+/*)", '', line).strip()

            try:
                # get the attribute:value pair
                attribute, value = line.split(':', 1)
                job[attribute.strip()] = value.strip()
            except ValueError:
                continue

        job.job_name = job['insert_job']

        return job
