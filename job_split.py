from jilutil.jil_parser import JilParser
from jilutil.auto_sys_job import AutoSysJob
from pathlib import Path

import pandas as pd
import re

class UnionFind:
    """Class to quickly join two sets together"""
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [1] * size

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x != root_y:
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

    def connected(self, x, y):
        return self.find(x) == self.find(y)

def create_empty_task(task_name, job_type):
    job = AutoSysJob(task_name)
    job.data["status"] = "DISABLED"
    job.data["job_type"] = job_type

    return job

def group_tasks(jobs):
    """Group tasks that depend of each other into their own list"""
    print(jobs)

jobs_to_migrate = pd.read_csv("marked_jobs.csv")
job_name_list = jobs_to_migrate["job_name"].tolist()

# .jil file with all of the jobs
full_jil_dump = Path("job_list.jil")
parsed_jobs = JilParser(None).parse_jobs_from_str(full_jil_dump.read_text())
job_id_dict = {}

# filter out tasks not marked by migration
filtered_jobs = []
for job in parsed_jobs["jobs"]:
    if job["insert_job"] in job_name_list or job["job_type"] == "BOX":
        filtered_jobs.append(job)


# map each job to a number id
for id, job in enumerate(filtered_jobs):
    job_id_dict[job["insert_job"]] = id

def extract_condition_job_names(condition_str):
    pattern = r's\((.*?)\)'
    matches = re.findall(pattern, condition_str)
    return matches

# transform conditions into an array
for job in filtered_jobs:
    if job.get("condition"):
        job["condition_array"] = extract_condition_job_names(job.get("condition"))

# join jobs linked by conditions or boxes into the same set
uf_set = UnionFind(len(filtered_jobs)+100)
for job in filtered_jobs:
    job_id = job_id_dict[job.get("insert_job")]

    if condition_array := job.get("condition_array"):
        for condition_task in condition_array:
            # add an empty task for tasks missing in dump
            if condition_task not in job_id_dict:
                condition_task_id = max(job_id_dict.values()) + 1
                job_id_dict[condition_task] = condition_task_id
                filtered_jobs.append(create_empty_task(condition_task, "CMD"))
            else:
                condition_task_id = job_id_dict[condition_task]

            uf_set.union(job_id, condition_task_id)

    if box_name := job.get("box_name"):
        box_job_id = job_id_dict[job.get("box_name")]
        uf_set.union(job_id, box_job_id)

# use the set id for each task to join them into a DAG
dag_dict = {}
for job in filtered_jobs:
    job_task_name = job["insert_job"]
    job_set_id = uf_set.find(job_id_dict[job_task_name])
    if job_set_id in dag_dict:
        dag_dict[job_set_id].append(job)
    else:
        dag_dict[job_set_id] = [job]

i = 1
for (dag_id, dag_data) in dag_dict.items():
    if len(dag_data) == 1 and dag_data[0]["job_type"] == "BOX":
        continue
    if len(dag_data) == 1:
        sub_folder = "single_task"
    else:
        sub_folder = "multiple_tasks"
    file = f"dags/{sub_folder}/dag_{i}.jil"
    with open(file, 'w') as f:
        for job in dag_data:
            if "condition_array" in job:
                del job["condition_array"]
            f.write(f"/* ----------------- {job['insert_job']} ----------------- */ \n \n")
            for attribute, value in job.items():
                if isinstance(value,list):
                    for v in value:
                        f.write(f"{str(attribute)}: {v} \n")
                else:
                    f.write(f"{str(attribute)}: {value} \n")
            f.write("\n \n")
    with open("task_to_id.csv", 'a') as f:
        for job in dag_data:
            if len(dag_data) > 1:
                job_type = "MULTI TASK"
            else:
                job_type = job["job_type"]
            f.write(f"{i},{job['insert_job']},{job_type}" + '\n')

    i += 1
