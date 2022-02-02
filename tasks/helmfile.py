import aws_infrastructure.tasks.library.instance_helmfile
import scope.config
from invoke import Collection
from pathlib import Path

import tasks.terraform.ecr

CONFIG_KEY = 'helmfile'
STAGING_LOCAL_HELMFILE_DIR = './.staging/helmfile'
STAGING_REMOTE_HELM_DIR = './.staging/helm'
STAGING_REMOTE_HELMFILE_DIR = './.staging/helmfile'

INSTANCE_TERRAFORM_DIR = './terraform/instance'
INSTANCE_NAME = 'instance'
HELMFILE_PATH = './helmfile/uwscope/helmfile.yaml'
HELMFILE_CONFIG_PATH = './helmfile/uwscope/helmfile_config.yaml'
SSH_CONFIG_PATH = Path(INSTANCE_TERRAFORM_DIR, INSTANCE_NAME, 'ssh_config.yaml')

FLASK_DEV_CONFIG_PATH = "./secrets/configuration/flask_dev.yaml"


# Requires information on accessing the ECR
def ecr_helmfile_values_factory(*, context):
    with tasks.terraform.ecr.ecr_read_only(context=context) as ecr_read_only:
        return {
            'registryUrl': ecr_read_only.output.registry_url,
            'registryUser': ecr_read_only.output.registry_user,
            'registryPassword': ecr_read_only.output.registry_password,
        }


# Requires flask_server configuration
def flask_dev_values_factory(*, context):
    flask_dev_config = scope.config.FlaskConfig.load(FLASK_DEV_CONFIG_PATH)

    return {
        "flaskConfig": flask_dev_config.encode()
    }


task_helmfile_apply = aws_infrastructure.tasks.library.instance_helmfile.task_helmfile_apply(
    config_key=CONFIG_KEY,
    ssh_config_path=SSH_CONFIG_PATH,
    staging_local_dir=STAGING_LOCAL_HELMFILE_DIR,
    staging_remote_dir=STAGING_REMOTE_HELMFILE_DIR,
    helmfile_path=HELMFILE_PATH,
    helmfile_config_path=HELMFILE_CONFIG_PATH,
    helmfile_values_factories={
        'ecr_generated': ecr_helmfile_values_factory,
        'flask_dev_generated': flask_dev_values_factory,
    },
)
task_helmfile_apply.__doc__ = 'Apply helmfile/uwscope/helmfile.yaml in the instance.'


ns = Collection('helmfile')
ns.add_task(task_helmfile_apply, 'apply')