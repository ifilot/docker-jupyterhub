# Configuration file for jupyterhub.

c = get_config()  #noqa

# set authenticator method
c.JupyterHub.authenticator_class = 'native'

# import native authenticator and specify its template
import os, nativeauthenticator
c.JupyterHub.template_paths = [f"{os.path.dirname(nativeauthenticator.__file__)}/templates/"]

# some password criteria
c.NativeAuthenticator.check_common_password = True
c.NativeAuthenticator.minimum_password_length = 8

# add re-captcha
c.NativeAuthenticator.recaptcha_key = "6LdjCoAoAAAAAFXyYpo4Tz99EQlNZCB3MK8-MQjy"
c.NativeAuthenticator.recaptcha_secret = "6LdjCoAoAAAAAGtrnSeZMXNdsXJQgWn_OY5qeamu"

# allow new users to self sign-up
c.NativeAuthenticator.open_signup = False

# how a new user is generated on the (containerized) OS
def pre_spawn_hook(spawner):
    username = 'jupyter-' + spawner.user.name
    try:
        import pwd
        pwd.getpwnam(username)
    except KeyError:
        import subprocess
        subprocess.check_call(['useradd', '-ms', '/bin/bash', username])

        # set path to home dir
        homedir = os.path.join('/home', username)

        # determine uid and gid of folder
        uid = os.stat(homedir).st_uid
        gid = os.stat(homedir).st_gid

        # create symbolic links to a skeleton template folder
        skeldir = os.path.join('/skel', 'notebooks')
        for item in os.listdir(skeldir):
            p = os.path.join(skeldir, item)
            if os.path.isdir(p) and item != '.' and item != '..':
                symlink = os.path.join(homedir, item)
                os.symlink(p, symlink)
                os.chown(symlink, uid, gid, follow_symlinks=False)

c.Spawner.pre_spawn_hook = pre_spawn_hook

# which notebook spwaner method is used
c.JupyterHub.spawner_class = 'systemd'

# restrict resources per user
c.SystemdSpawner.mem_limit = '1G'
c.SystemdSpawner.cpu_limit = 1.0
c.SystemdSpawner.user_workingdir = '/home/jupyter-{USERNAME}'
c.SystemdSpawner.username_template = 'jupyter-{USERNAME}'
c.SystemdSpawner.disable_user_sudo = True
c.SystemdSpawner.default_shell = '/bin/bash'

# specify which username(s) can act as administrators
c.Authenticator.admin_users = {'admin'}

# show resource details per user
c.ResourceUseDisplay.track_cpu_percent = True