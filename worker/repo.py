""" GitLab projects handling module. """


import os
import subprocess
import hashlib
import gitlab

COLLECTED = 1
BAD_CALL = 2


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

    try:
        with open(zip_arts, "wb") as file:
            job.artifacts(streamed=True, action=file.write)
        subprocess.run(["unzip", "-qo", zip_arts], check=True)
    except (gitlab.exceptions.GitlabGetError, subprocess.CalledProcessError):
        return BAD_CALL, job.status

    os.unlink(zip_arts)

    return COLLECTED, job.status


def get_group_artifacts(instance, game, group_name):
    """ Collect group projects artifacts by game's name. """

    group = get_group(instance, group_name)
    projects = get_group_projects(instance, group)

    results = []

    print("START ARTIFACTS COLLECTION")

    for prj in projects:
        project = get_project(instance, group, prj.name)
        job = get_last_job(project, game)

        if job is None:
            print(f"THERE IS NO {game} BRANCH JOBS FOR {project.name}")
            continue

        developer = None
        members = project.members.list(all=True)

        for mmbr in members:
            member = project.members.get(mmbr.id)
            if member.access_level == gitlab.DEVELOPER_ACCESS:
                developer = member
                break

        if developer is not None:
            user_result = [developer.name, "@" + developer.username]
            results.append(user_result)
            if check_md5(os.path.abspath("cfg/.gitlab-ci.students.yml"),
                         project, game, ".gitlab-ci.yml") is False:
                print(f"CORRUPTED CI FOUND FOR {user_result[1]}")
                continue
            print(f"CORRECT CI FOUND FOR {user_result[1]}")
            status = get_artifacts(project, job)

            if status[0] == COLLECTED:
                print(f"ARTIFACTS FOR {user_result[1]} ARE COLLECTED")
            elif status[0] == BAD_CALL:
                print(f"THERE ARE NO ARTIFACTS FOR {user_result[1]}")
        else:
            print(f"THERE IS NO DEVELOPER FOR {project.name}")

    print("FINISH ARTIFACTS COLLECTION\n")

    return results
