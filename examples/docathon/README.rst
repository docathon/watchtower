To generate project information::

  python extract_project_information.py filename

where filename is the csv file containing the projects registration
information.

To fetch commits::

  python fetch_project_commits.py filename --auth USERNAME:TOKEN

This not only attempts to fetch the commits, but also writes a file called
".downloaded_projects", containing org and repo name for all projects. This is
then used to plot commits for each project.

After, and only after, to plot commits run the following::

  python plot_commits.py
