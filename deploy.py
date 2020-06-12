#!/usr/bin/env python

import os
import subprocess
from pathlib import Path

NAME = 'parents'
TARGET = 'ubuntu@13.209.3.115'
DOCKER_IMAGE_TAG = f'raccoonhj33/{NAME}'
DOCKER_PORT = '888:8000'
SECRETS_FILE = os.path.join(os.path.join(str(Path.home()), NAME), 'secrets.json')


def run(cmd, ignore_error=False):
    process = subprocess.run(cmd, shell=True)

    if not ignore_error:
        process.check_returncode()


def ssh_run(cmd, ignore_error=False):
    run(f'ssh -o StrictHostKeyChecking=no -i ~/.ssh/mini.pem {TARGET} {cmd}', ignore_error=ignore_error)


def local_build_push():
    run(f'poetry export -f requirements.txt > requirements.txt')
    run(f'docker system prune --force')
    run(f'docker build -t {DOCKER_IMAGE_TAG} .')
    run(f'docker push {DOCKER_IMAGE_TAG}')


def server_init():
    ssh_run(f'sudo apt -y update')
    ssh_run(f'sudo apt -y dist-upgrade')
    ssh_run(f'sudo apt -y autoremove')
    ssh_run(f'sudo apt -y install docker.io')


def server_pull_run():
    ssh_run(f'sudo docker pull {DOCKER_IMAGE_TAG}')
    ssh_run(f'sudo docker stop {NAME}', ignore_error=True)
    ssh_run('sudo docker run {options} {tag} /bin/bash'.format(
        options=f'--rm -it -d --name {NAME} -p {DOCKER_PORT}',
        tag=DOCKER_IMAGE_TAG
    ))


def copy_secrets():
    run(f'scp -i ~/.ssh/mini.pem {SECRETS_FILE} {TARGET}:/tmp')
    ssh_run(f'sudo docker cp /tmp/secrets.json {NAME}:/srv/{NAME}')


def server_runserver():
    ssh_run(f'sudo docker exec {NAME} python manage.py collectstatic --noinput')
    ssh_run(f'sudo docker exec -d {NAME} supervisord -c /srv/{NAME}/.config/supervisord.conf')


if __name__ == '__main__':
    try:
        print('--- Deploy start! ---')
        local_build_push()
        server_init()
        server_pull_run()
        copy_secrets()
        server_runserver()
        print('--- Deploy completed! ---')
    except subprocess.CalledProcessError as e:
        print('e.cmd, e.returncode, e.output, e.stdout, e.stderr >> ')
        print(e.cmd, e.returncode, e.output, e.stdout, e.stderr)
