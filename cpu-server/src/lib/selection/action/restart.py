from lib.utils import cleanup

def restart_action(state):
    cleanup(state)
    return 'LAUNCH_RESPONDER'
