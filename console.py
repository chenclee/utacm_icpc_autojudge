def start_contest(args):
    pass


def add_duration(args):
    pass


def freeze_scoreboard(args):
    pass


def unfreeze_scoreboard(args):
    pass


def view_recent_submissions(args):
    pass


def view_clarification_queue(args):
    pass


def respond_clarification(args):
    pass


if __name__ == '__main__':
    supported_functions = {
        'start':
            (start_contest, 'start [delay] [duration] [prob_dir] [sub_dir]'),
        'add_duration':
            (add_duration, 'add_duration [duration]'),
        'freeze_scoreboard':
            (freeze_scoreboard, 'freeze_scoreboard'),
        'unfreeze_scoreboard':
            (unfreeze_scoreboard, 'unfreeze_scoreboard'),
        'view_recent_submissions':
            (view_recent_submissions, 'view_recent_submissions'),
        'view_clarification_queue':
            (view_clarification_queue, 'view_clarification_queue'),
        'respond':
            (respond_clarification, 'respond [clarif_id] [response]')
    }

    while True:
        cmd_line = raw_input().strip()
        cmd = cmd_line.split()
        try:
            supported_functions[cmd[0]][0](*cmd[1:])
        except Exception:
            if cmd_line != '':
                if cmd[0] in supported_functions:
                    print 'Usage:', supported_functions[cmd[0]][1]
                elif cmd[0] == 'help':
                    print 'Supported Commands:'
                    for func in supported_functions:
                        print '    ', supported_functions[func][1]
                else:
                    print 'Fuck you Tres:', cmd[0]
