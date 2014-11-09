import os
import json

from contest import Contest
from judge import Judge


contest = None
judge = None


def start_contest(contest_dir, delay=15*60):
    global contest
    global judge
    contest_cfg = None
    print 'Loading contest config files...'
    with open(os.path.join(contest_dir, 'config.txt'), 'r') as in_file:
        contest_cfg = eval(in_file.read())
        print 'Contest configuration:'
        print json.dumps(contest_cfg, indent=4)

    contest = Contest(int(delay), contest_cfg['duration'],
                      contest_cfg['prob_ids'], contest_cfg['penalty'])
    judge = Judge(contest, contest_cfg['prob_ids'], contest_dir)


def add_duration(duration):
    contest.extend(int(duration))


def debug():
    print '======== DEBUG ========'
    print 'Contest is currently running:', contest.is_running()
    rem = contest.remaining_time()
    print 'Remaining time in contest: %02d:%02d:%02d' % (
        int(rem / 60 / 60), int(rem / 60 % 60), int(rem % 60))
    print 'Scoreboard:'
    print json.dumps(contest.get_scoreboard(), indent=4)
    print 'Clarifications:'
    print json.dumps(contest.get_clarifs(-1), indent=4)
    print '====== END DEBUG ======'


def submit_clarif(user_id, prob_id):
    contest.submit_clarif(user_id, prob_id, raw_input())


def freeze_scoreboard():
    contest.freeze_scoreboard(True)


def unfreeze_scoreboard():
    contest.freeze_scoreboard(False)


def view_recent_submissions():
    # XXX
    submissions = contest.get_submissions()
    print submissions[len(submissions)-10:]


def view_clarification_queue():
    for index, clarif in enumerate(contest.get_clarifs(-1)):
        if clarif[3] is None:
            prompt_clarification(clarif, index)


def prompt_clarification(clarif, clarif_id):
    print clarif[2]
    while True:
        print 'Response options follow:'
        print '0) "Reread the problem statement"'
        print '1) "Come talk to the administers"'
        print '2) Answer and respond to all'
        print '3) Do not answer at this time'
        option = -1
        try:
            option = int(raw_input())
        except Exception:
            print 'Invalid option. Try again.'
            continue
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
        'start_contest':
            (start_contest, 'start_contest contest_dir [delay]'),
        'add_duration':
            (add_duration, 'add_duration duration'),
        'debug':
            (debug, 'debug'),
        'submit_clarif':
            (submit_clarif, 'submit_clarif user_id prob_id'),
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
        except Exception as err:
            print err
            if cmd_line != '':
                if cmd[0] in supported_functions:
                    print 'Usage:', supported_functions[cmd[0]][1]
                elif cmd[0] == 'help':
                    print 'Supported Commands:'
                    for func in supported_functions:
                        print '    ', supported_functions[func][1]
                else:
                    print 'You done goofed:', cmd[0]
        if cmd_line != '':
            print ''
