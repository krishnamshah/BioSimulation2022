# Setting up your BioSim Project on GitLab

1. On your computer, pull all updates from the inf200-course-materials repository.
    - Under `january_block/biosim_template` you will now find several directories (`biosim`, `examples`, `tests` and a `sample.gitignore` file). 
1. One of the two partners, shall now do the following on GitLab
    1. In your `Axx_FirstName1_FirstName2` group on GitLab, create a new project.
    1. Select "Create blank project".
	1. Choose project name `BioSim Axx FirstName1 FirstName2`. The corresponding "Project slug" will then be `biosim-axx-firstname1-firstname2`.  Here, `xx` is your group number (with leading zero!) and `FirstName1` and `FirstName2` your first names as in the group name.
    1. Check off for "Intialize repository with a README".
1. One of you then does the following on your computer:
    1. Start PyCharm and select `Get from VCS`
	1. Paste the URL from the GitLab clone button and choose a sensible location on your computer.
	1. Once PyCharm has cloned and opened the project, ensure that the correct Python interpreter is chosen (the `inf200` conda environment).
	1. You should now have the project in folder `biosim-axx-firstname1-firstname2` in your repo.
	1. Now copy all directories and the `sample.gitignore` file from the `biosim_template` folder into the project folder. They should show up in PyCharm after a little moment.
	1. Rename `sample.gitignore` to `.gitignore` by right-clicking the file name in PyCharm and chosing Refactor > Rename.
	1. Commit all new files to Git (either in PyCharm, GitAhead or your preferred git program) and push to GitLab.
1. Now the other partner can clone the project in PyCharm as described above and you are ready to go.
