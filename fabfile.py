import sys
import os
import deploy_config

# Add current directory to path.
local_dir = os.path.dirname(__file__)
sys.path.append(local_dir)

from fabric.api import *

path = '/home/crisisnet/suckapy'
venv = '/home/crisisnet/suckapy/venv'
release_file = '/home/crisisnet/releases.suckapy'

@task
def staging():
    env.host_string = deploy_config.STAGING_HOST
    env.user = deploy_config.STAGING_USER
    env.password = deploy_config.STAGING_PASSWORD
    env.key_filename = ''
    env.branch = 'development'
    env.upstart_script = 'suckapy.conf'
    env.settings_file = 'staging_settings.py'
    env.app_env = 'staging'


@task
def production():
    env.host_string = deploy_config.PROD_HOST
    env.user = deploy_config.PROD_USER
    env.password = deploy_config.PROD_PASSWORD
    env.key_filename = ''
    env.branch = 'master'
    env.upstart_script = 'suckapy_prod.conf'
    env.settings_file = 'production_settings.py'
    env.app_env = 'production'
    env.port = 15922


def install_deps():
    """
    Installs os and base packages.
    """
    deps = ['build-essential python-dev python-pip libevent-dev libpq-dev libxml2-dev libxslt1-dev git']
    for dep in deps:
        sudo('apt-get install -y %s' % dep)
    sudo('pip install virtualenv')


def check_upstart():
    """
    Checks if uwsgi upstart exists; if not, upstart job is created.
    If it exists and is different from the checked-in version, it's updated.
    """
    sudo('test -f /etc/init/suckapy.conf || cp etc/suckapy.conf /etc/init')
    sudo('diff etc/suckapy.conf /etc/init/suckapy.conf || cp etc/suckapy.conf /etc/init')


@task
@parallel
def deploy(branch=None):
    branch = branch or env.branch
    install_deps()
    # Check for first deploy.
    run("test -d %s || git clone https://github.com/ushahidi/suckapy.git %s" % (path, path))
    
    # Check for virtualenv.
    run('test -d %s || virtualenv %s' % (venv, venv))

    with cd(path):
        #run('git branch --set-upstream %s origin/%s' % (branch, branch))
        do_release(branch)
        record_release()



def copy_private_files():
    """
    Files that we shouldn't include in the public repo because they contain 
    sensitive information (third-party service API keys, db connect info, etc)
    """
    settings_file = '/src/config/' + env.settings_file
    put(local_dir + settings_file,path + settings_file,mirror_local_mode=True)


def do_release(branch):
    run('git fetch')
    run('git checkout %s && git pull' % branch)
    with prefix('source %s/bin/activate' % venv):
        run('pip install -r requirements.txt')
    copy_private_files()
    check_upstart()
    sudo('service suckapy stop; service suckapy start SUCKAPY=%s' % env.app_env)


def record_release():
    """
    Records the git commit version so that we can rollback.
    """
    current_release = run("git rev-parse HEAD")
    # Note that this uses warn_only kwarg which will still fail in older 
    # versions of fabric.
    last_release = run("tail -n 1 %s" % release_file, warn_only=True)
    if last_release.failed:
        run("echo %s > %s" % (current_release, release_file))
    elif current_release != last_release:
        run("echo %s >> %s" % (current_release, release_file))


@task
@parallel
def rollback(num=1):
    """
    Rollsback git version to a previous release.
    """
    num = num + 1
    with cd(path):
        release_version = run("tail -n %s %s | head -n 1" % (num, release_file))
        run('git checkout %s' % release_version)
        do_release()
