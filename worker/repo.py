""" GitLab projects handling module. """


import os
import subprocess
import hashlib
import gitlab

COLLECTED = 1
BAD_REQUEST = 2
BAD_CALL = 3


def get_group(instance, name):
    """ Get group by it's name. """

    group = None

    groups = instance.groups.list(all=True)
    for grp in groups:
        if grp.name == name:
            group = grp
            break

    return group


def get_group_projects(instance, group):
    """ Get group's projects. """

    group = instance.groups.get(group.id)
    projects = group.projects.list(all=True)

    return projects


def get_project(instance, group, name):
    """ Get project by it's name. """

    project = None

    projects = get_group_projects(instance, group)
    for prj in projects:
        if prj.name == name:
            project = instance.projects.get(prj.id)
            break

    return project


def get_last_job(project, ref):
    """ Get project's last job by ref name. """

    job = None

    jobs = project.jobs.list(all=True)
    for jb in jobs:
        if jb.ref == ref:
            job = jb
            break

    return job


def check_md5(master, project, ref, user):
    """ Check user file's identity to master file. """

    master_file = open(master, "rt").read()
    master_md5 = hashlib.md5(master_file.encode("utf-8")).hexdigest()
    user_file = project.files.get(file_path=user, ref=ref)
    user_md5 = hashlib.md5(user_file.decode()).hexdigest()

    if master_md5 != user_md5:
        return False

    return True


def get_artifacts(project, job):
    """ Get job's artifacts. """

    job = project.jobs.get(job.id)
    zip_arts = job.user.get("username") + ".zip"

    if job.status == "success":
        try:
            with open(zip_arts, "wb") as file:
                job.artifacts(streamed=True, action=file.write)
            subprocess.run(["unzip", "-qo", zip_arts], check=True)
        except (gitlab.exceptions.GitlabGetError, subprocess.CalledProcessError):
            return BAD_CALL

        os.unlink(zip_arts)

        return COLLECTED

    return BAD_REQUEST
