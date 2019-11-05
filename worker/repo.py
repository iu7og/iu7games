""" GitLab projects handling module. """


import os
import subprocess
import gitlab


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


def get_last_success_job(project, ref):
    """ Get project's last success job by ref name. """

    success_job = None

    jobs = project.jobs.list(all=True, ref=ref)
    for job in jobs:
        if job.status == "success" and job.ref == ref:
            success_job = job
            break

    return success_job


def get_artifacts(project, success_job):
    """ Get success job's artifacts. """

    job = project.jobs.get(success_job.id)
    zip_arts = job.user.get("username") + ".zip"

    try:
        with open(zip_arts, "wb") as file:
            job.artifacts(streamed=True, action=file.write)
        subprocess.run(["unzip", "-qo", zip_arts])
    except gitlab.exceptions.GitlabGetError:
        pass
    os.unlink(zip_arts)
