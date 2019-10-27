""" Worker for IU7Games project. """


import gitlab


def create_issue(instance, project_id, title, description):
    """ Create issue on GitLab instance. """
    project = instance.projects.get(project_id)
    project.issues.create(
        {
            'title': title,
            'description': description
        },
        project_id=project_id)
    print("Created Issue", title)


def worker():
    """ API Worker to collect students' repos' artifacts. """
    gl = gitlab.Gitlab.from_config("gitiu7", ["./api_config.cfg"])
    gl.auth()
    create_issue(gl, 2546, "Тестовое issue, сгенерированное при помощи API",
                 "Это issue было создано при помощи API.")


if __name__ == "__main__":
    worker()
