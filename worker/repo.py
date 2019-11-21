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


def get_success_job(project, ref):
    """ Get project's last sucess job by ref name. """

    success_job = None

    jobs = project.jobs.list(all=True)
    for job in jobs:
        if job.ref == ref and job.status == "success":
            success_job = job
            break

    return success_job


def get_deploy_job(project, game, ref):
    """ Get game deploy job. """

    deploy_job = None

    jobs = project.jobs.list(all=True)
    for job in jobs:
        if job.ref == ref and job.status == "success" and job.name == f"deploy_{game}":
            deploy_job = job
            break

    return deploy_job


def get_job_date(job):
    """ Get job finishing time in HH:MM:SS DD.MM.YYYY format. """

    job_date = job.finished_at[0:10].split("-")
    job_date[0], job_date[2] = job_date[2], job_date[0]
    job_date = ".".join(job_date)

    job_time = job.finished_at[11:19]

    job_status = f"{job_time} {job_date}"

    return job_status


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
        return BAD_CALL

    os.unlink(zip_arts)

    return COLLECTED


def get_group_artifacts(instance, game, group_name):
    """ Collect group projects artifacts by game's name. """

    group = get_group(instance, group_name)
    projects = get_group_projects(instance, group)

    results = []

    print("START ARTIFACTS COLLECTION")

    for prj in projects:
        project = get_project(instance, group, prj.name)
        job = get_success_job(project, game)

        if job is None:
            print(f"THERE ARE NO OK JOBS FOR {game} BRANCH IN {project.name}")
            continue

        developer = None
        members = project.members.list(all=True)

        for mmbr in members:
            member = project.members.get(mmbr.id)
            if member.access_level == gitlab.DEVELOPER_ACCESS:
                developer = member
                break

        if developer is not None:
            user_result = [developer.name, "@" +
                           developer.username, get_job_date(job)]
            results.append(user_result)
            if check_md5(os.path.abspath("cfg/.gitlab-ci.students.yml"),
                         project, game, ".gitlab-ci.yml") is False:
                print(f"CORRUPTED CI FOUND FOR {user_result[1]}")
                continue
            print(f"CORRECT CI FOUND FOR {user_result[1]}")
            status = get_artifacts(project, job)

            if status == COLLECTED:
                print(f"ARTIFACTS FOR {user_result[1]} ARE COLLECTED")
            elif status == BAD_CALL:
                print(f"THERE ARE NO ARTIFACTS FOR {user_result[1]}")
        else:
            print(f"THERE IS NO DEVELOPER FOR {project.name}")

    print("FINISH ARTIFACTS COLLECTION\n")

    return results
