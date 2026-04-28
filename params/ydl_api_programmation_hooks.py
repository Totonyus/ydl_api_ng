import logging

# Called when a programmation is automatically deleted
def purged_programmation_handler(purged_programmations = None, **kwargs):
    return

# Called when a download is launched by the daemon
def post_launch_handler(download_manager = None, **kwargs):
    return

# Called when a programmation is stopped by the daemon
def post_termination_handler(terminated_job = None, **kwargs):
    return
