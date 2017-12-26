# Restaurant instructions. - 06/21/2017

## Introduction
This project provides a list of menu items within a variety of restaurants. It 
also provides a third-party user registration and authentication system. 
Registered users will have the ability to post, edit, and delete their own items.


## Installation
First you must have Python, Git, Vagrant, and a Virtual Machine installed.

Right click inside the folder containing this project. Press on `Git Bash Here`. 
Once the command prompt is up, open the virtual machine.
```
$ vagrant up
...
$ vagrant ssh
```

On your virtual machine, change your directory to the current project file.
Run the command:
```
$ python project.py
```

Congratulations, your project is now running.


## Known Errors
#### filter() vs filter_by()
If you get an error while attempting to start the project that looks like this:
```
TypeError: filter() got an unexpected keyword argument
```

Change `filter()` to `filter_by()` in all instances at the end of the 
`project.py` file and restart the project.
