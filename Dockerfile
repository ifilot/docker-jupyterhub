FROM jupyterhub/jupyterhub

# install defualt platform
RUN pip3 install notebook jupyterlab numpy scipy pandas matplotlib

# install plugins for JupyterHub
RUN pip3 install jupyterhub-systemdspawner
RUN pip3 install jupyterhub-nativeauthenticator
RUN pip3 install jupyter-resource-usage
RUN pip3 install jupyterlab-myst

# install systemd
RUN apt update
RUN apt install -y systemd sudo init

# Kill all the things we don't need
RUN find /etc/systemd/system \
    /lib/systemd/system \
    -path '*.wants/*' \
    -not -name '*journald*' \
    -not -name '*systemd-tmpfiles*' \
    -not -name '*systemd-user-sessions*' \
    -exec rm \{} \;

# create folder to hold sudo users
RUN mkdir -p /etc/sudoers.d

# create folder to hold skeleton notebooks
RUN mkdir -pv /skel/notebooks/tests
RUN chmod 755 /skel /skel/notebooks
COPY notebooks/tests /skel/notebooks/tests
RUN chmod 755 /skel /skel/notebooks/tests
RUN chmod 644 /skel/notebooks/tests/*

RUN systemctl set-default multi-user.target

STOPSIGNAL SIGRTMIN+3

# copy configuration files
COPY config/jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py

# copy service files
COPY services/jupyterhub_launch.service /etc/systemd/system/jupyterhub_launch.service
RUN chmod 644 /etc/systemd/system/jupyterhub_launch.service
RUN systemctl enable jupyterhub_launch

CMD ["/bin/bash", "-c", "exec /sbin/init --log-target=journal 3>&1"]