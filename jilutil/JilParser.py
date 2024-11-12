"""AutoSys JIL Utility (https://github.com/mscribellito/JIL-Utility)"""
from __future__ import annotations

from re import match
from typing import Dict, List

from jilutil.AutoSysJob import AutoSysJob

class JilParser:

    """Class that parses JIL into jobs"""

    job_comment = '/* -----------------'

    def __init__(self, path):
        """Instantiates a new instance"""

        self.path = path

    def read_jil(self):
        """Reads JIL from a file"""

        # list of trimmed & not empty lines in file
        lines = []

        with open(self.path, 'r') as f:
            for line in f:
                # remove leading & trailing whitespace
                line = line.strip()
                # check if line is empty
                if not line:
                    continue
                lines.append(line.strip())

        return lines

    def parse_jobs_from_str(self, input_str: str | None) -> Dict[str, List[AutoSysJob]]:
        r"""Read directly from a multiline JIL string and return a dictionary like {'jobs': [AutoSysJob, ...]}

        ```pycon
        >>> JilParser(None).parse_jobs_from_str('')
        {'jobs': []}
        >>> JilParser(None).parse_jobs_from_str(None)
        {'jobs': []}
        >>> val = '''\ninsert_job: TEST.ECHO
        ... job_type: CMD
        ... owner: waadm
        ... machine: orasvr19
        ... command: echo "Hello World"'''
        >>> JilParser(None).parse_jobs_from_str(val)
        {'jobs': [{'insert_job': 'TEST.ECHO', 'job_type': 'CMD', 'owner': 'waadm', 'machine': 'orasvr19', 'command': 'echo "Hello World"'}]}
        >>> val = '''insert_job: TEST.ECHO  job_type: CMD  /* INLINE COMMENT */
        ... owner: waadm
        ... /* MULTILINE
        ...     COMMENT */
        ... machine: orasvr19
        ... command: echo "Hello World"'''
        >>> JilParser(None).parse_jobs_from_str(val)
        {'jobs': [{'insert_job': 'TEST.ECHO', 'job_type': 'CMD', 'owner': 'waadm', 'machine': 'orasvr19', 'command': 'echo "Hello World"'}]}

        ```
        """
        output = {"jobs": []}
        if not input_str:
            return output

        jobs = self.find_jobs(input_str.splitlines())
        if parsed_jobs := [AutoSysJob.from_str('\n'.join(job)) for job in jobs]:
            output['jobs'] = parsed_jobs
        return output


    def find_jobs(self, lines):
        """Finds jobs from lines"""

        jobs = [[]]
        i = -1

        for line in lines:
            # check if the line contents indicate a new job
            if line.startswith(self.job_comment):
                # find job start match
                matches = match(AutoSysJob.job_start_regex, line)
                # if match found, create new list for job lines & increment number of jobs
                if matches:
                    jobs.append([])
                    i += 1
            # is not a new job, add contents of line
            else:
                jobs[i].append(line)

        return jobs

    def parse_jobs(self):
        """Parses jobs from JIL"""

        lines = self.read_jil()
        raw_jobs = self.find_jobs(lines)
        parsed_jobs = []

        for definition in raw_jobs:
            # create new job from list of strings
            job = AutoSysJob.from_str('\n'.join(definition))
            parsed_jobs.append(job)

        return parsed_jobs
