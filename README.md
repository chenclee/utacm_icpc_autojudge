utacm_icpc_autojudge
====================

Auto Judge for UTACM's Programming Contests

docker-sandbox How-To:
1) Install docker
2) Download ubuntu:14.04 container
3) Execute update_docker.sh
4) May need to add 'GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"' to /etc/default/grub
5) Run server.py with sudo access

Running Sample Contest:
sudo python server.py --admin_whitelist='admin@example.com' --contest_dir='sample_contest' --delay=15 --port=8001 --client_id='YOUR_CLIENT_ID' --client_secret='YOUR_CLIENT_SECRET' --redirect_url='http://localhost:8001/auth/login'

Prevent Fork Bombs:
1) Open /etc/init/docker.conf
2) Change nproc to "limit nproc 16 160"
