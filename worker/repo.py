"""
    Модуль для работы над GitLab-проектами.
"""


import os
import subprocess
import hashlib
import gitlab

from dateutil import parser

COLLECTED = 1
BAD_CALL = 2


def get_group(instance, name):
    """
        Получение GitLab-группы по имени группы.
    """

    group = None

    groups = instance.groups.list(all=True)
    for grp in groups:
        if grp.name == name:
            group = grp
            break

    return group


def get_group_projects(instance, group):
    """
        Получение GitLab-проектов внутри группы.
    """

    group = instance.groups.get(group.id)
    projects = group.projects.list(all=True)

    return projects


def get_project(instance, group, name):
    """
        Получение GitLab-проекта по имени проекта.
    """

    project = None

    projects = get_group_projects(instance, group)
    for prj in projects:
        if prj.name == name:
            project = instance.projects.get(prj.id)
            break

    return project


def get_success_job(project, ref):
    """
        Получение последнего успешного job'а в ветке.
    """

    success_job = None

    jobs = project.jobs.list(all=True)
    for job in jobs:
        if job.ref == ref and job.status == "success":
            success_job = job
            break

    return success_job


def get_deploy_job(project, game, ref):
    """
        Получение job'а со статусом "deploy".
    """

    deploy_job = None

    jobs = project.jobs.list(all=True)
    for job in jobs:
        if job.ref == ref and job.status == "success"and job.name == f"deploy_{game}":
            deploy_job = job
            break

    return deploy_job


def get_job_date(job):
    """
        Получение даты последнего зверешения job'а в формате ЧЧ:ММ:СС ДД.ММ.ГГГ.
    """

    job_date = job.finished_at[0:10].split("-")
    job_date[0], job_date[2] = job_date[2], job_date[0]
    job_date = ".".join(job_date)

    job_time = job.finished_at[11:19]

    job_status = f"{job_time} {job_date}"

    return parser.parse(job_status, dayfirst=True)


def check_md5(master, project, ref, user):
    """
        Проверка md5-суммы файла в репозитории пользователя
        с файлом в основном репозитории.
    """

    master_file = open(master, "rt").read()
    master_md5 = hashlib.md5(master_file.encode("utf-8")).hexdigest()
    user_file = project.files.get(file_path=user, ref=ref)
    user_md5 = hashlib.md5(user_file.decode()).hexdigest()

    if master_md5 != user_md5:
        return False

    return True


def get_artifacts(project, job):
    """
        Получение артефактов job'ы.
    """

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
    """
        Получение артефактов со всех проектов группы из определенной ветки.
    """

    group = get_group(instance, group_name)
    projects = get_group_projects(instance, group)

    results = []

    print("START ARTIFACTS COLLECTION")

    for ind, prj in enumerate(projects):
        project = get_project(instance, group, prj.name)
        job = get_success_job(project, game)

        if job is None:
            print(f"THERE ARE NO OK JOBS FOR {game} BRANCH IN {project.name}")
            continue

        developer = None
        members = project.members.list(all=True)

        members_list = []

        for mmbr in members:
            member = project.members.get(mmbr.id)
            if member.access_level == gitlab.DEVELOPER_ACCESS:
                members_list.append(member)

        if group_name == "iu7-bachelors-2023-practice-2020-iu7games":
            developer = members_list[0]
            developer.name = project.name[len(group_name) + 1:]
            username = ""
            for member in members_list:
                username += f"@{member.username}, "
            developer.username = username[:-2]
        else:
            developer = members_list[0]
            developer.username = f"@{developer.username}"

        if developer is not None:
            user_result = [str(ind), developer.name, developer.username, get_job_date(job)]
            results.append(user_result)
            if check_md5(os.path.abspath("cfg/.gitlab-ci.students.yml"),
                         project, game, ".gitlab-ci.yml") is False:
                print(f"CORRUPTED CI FOUND FOR {user_result[2]}")
                continue
            print(f"CORRECT CI FOUND FOR {user_result[2]}")
            status = get_artifacts(project, job)

            if status == COLLECTED:
                print(f"ARTIFACTS FOR {user_result[2]} ARE COLLECTED")
            elif status == BAD_CALL:
                print(f"THERE ARE NO ARTIFACTS FOR {user_result[2]}")
        else:
            print(f"THERE IS NO DEVELOPER FOR {project.name}")

    print("FINISH ARTIFACTS COLLECTION\n")

    return results
