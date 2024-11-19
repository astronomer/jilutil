"""AutoSys JIL Utility (https://github.com/mscribellito/JIL-Utility)"""
import re
from collections import UserDict


class AutoSysJob(UserDict):
    r"""Regex pattern for matching job start comments
    >>> re.match(AutoSysJob.job_start_regex, 'insert_job: FOO\n\nbar: baz').group(1)
    'FOO'
    """

    """Class that represents a job within AutoSys and its attributes"""

    default_attributes = {
        'insert_job': '',
        'job_type': '',
        'box_name': '',
        'command': '',
        'machine': '',
        'owner': '',
        'permission': '',
        'date_conditions': '',
        'days_of_week': '',
        'start_times': '',
        'condition': '',
        'description': '',
        'std_out_file': '',
        'std_err_file': '',
        'alarm_if_fail': '',
        'group': '',
        'application': '',
        'send_notification': '',
        'notification_msg': '',
        'success_codes': '',
        'notification_emailaddress': '',
        'auto_delete': '',
        'box_terminator': '',
        'chk_files': '',
        'exclude_calendar': '',
        'job_load': '',
        'job_terminator': '',
        'max_exit_status': '',
        'max_run_alarm': '',
        'min_run_alarm': '',
        'n_retrys': '',
        'priority': '',
        'profile': '',
        'run_window': '',
        'term_run_time': ''
    }

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
        job_str += 'insert_job: {}   job_type: {}\n'.format(atts['insert_job'], atts['job_type'])
        del atts['insert_job']
        del atts['job_type']

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
        
        NOTIFICATION_EMAILADDRESS = "notification_emailaddress"

        job = cls()

        # force job_type onto a new line
        jil = jil.replace('job_type', '\njob_type', 1)
        jil = jil.replace('\r\n', '\n')

        # split lines and strip line if not empty
        lines = [line.strip() for line in jil.split('\n') if line.strip() != '']

        multiline_comment_mode = False
        email_address_list = []
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
                if attribute == NOTIFICATION_EMAILADDRESS:
                    email_address_list.append(value)
                else:
                    job[attribute.strip()] = value.strip()
            except ValueError:
                continue
            
        job[NOTIFICATION_EMAILADDRESS] = email_address_list
        job.job_name = job['insert_job']

        return job
