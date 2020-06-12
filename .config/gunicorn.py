daemon = False
chdir = '/srv/parents/'
bind = 'unix:/run/parents.sock'
accesslog = '/var/log/gunicorn/parents-access.log'
errorlog = '/var/log/gunicorn/parents-error.log'