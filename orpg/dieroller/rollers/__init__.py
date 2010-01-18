import os, os.path

rollers = 'orpg.dieroller.rollers'
rollers_path = __import__(rollers, {}, {}, ['orpg.dieroller.rollers'.split('.')[-1]]).__path__

for roller in os.listdir(os.path.abspath(os.path.dirname(__file__))):
    if roller.endswith('.py') and not roller.startswith('__'):
        __import__("%s.%s" % (rollers, roller.split('.')[0]))
