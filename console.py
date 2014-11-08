def start_contest(delay, duration, prob_dir, sub_dir):
    # contest = Contest(delay, duration, prob_dir)
    # judge = Judge(contest, )
    pass

def add_duration(duration):
    contest.extend(duration)

def freeze_scoreboard():
    contest.freeze_scoreboard(TRUE)

def unfreeze_scoreboard():
    contest.freeze_scoreboard(FALSE)

def view_recent_submissions():
    # XXX
    submissions = contest.get_submissions()
    print submissions[len(submissions)-10:]

def view_clarification_queue():
    for index,clarif in enumerate(contest.get_clarifs(-1)):
        if clarif[3] == None:
            prompt_clarification(clarif, index)

def prompt_clarification(clarif, clarif_id):
    print clarif[2]
    while True:
        print 'Response options follow:'
        print '0) \'Reread the problem statement\''
        print '1) \'Come talk to the administers\''
        print '2) Answer and respond to all'
        print '3) Do not answer at this time'
        option = raw_input()
        if option == 0:
            contest.respond_clarif(clarif_id, 'Reread the problem statement.')
            return
        elif option == 1:
            contest.respond_clarif(clarif_id, 'Come talk to the administers.')
            return
        elif option == 2:
            print 'Please write out your response:'
            contest.respond_clarif(clarif_id, raw_input(), False)
            return
        elif option == 3:
            return
        else:
            print 'Invalid option. Try again.'

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
                    print 'You done goofed:', cmd[0]
