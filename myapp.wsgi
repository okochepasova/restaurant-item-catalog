import sys
sys.path.insert(0, '/home/grader/projects/restaurant-item-catalog')

from project import app as application

application.secret_key = 'super_secret_key'
