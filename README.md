# Alfred Make Template

This is a template for new workflows for the [Alfred app][] for macOS. 

It comes with a [Makefile](Makefile) that contains to help you develop your workflow or create a deployable `.alfredworkflow` file.

It is fairly simple, but I plan on using it as a root for other templates.

[Alfred app]: https://alfredapp.com/

# Using this template

## Forking

First, create a repo from this template. This will allow you to create a repo on your GitHub account for your new workflow.

Then, clone your repo:

```sh
git clone https://github.com/yourusername/yourreponame
cd yourreponame
```

## Developing

### 1. Calling de-template

There are some files that are specific to the template repo, and aren't needed in forked workflows. To remove them, call [scripts/de-template]():

```sh
scripts/detemplate
```

### 2. Update Makefile

Update the top of the `Makefile` in any text editor and change the name, and include any files you've added that your workflow needs to run.

For example, if you plan on including `search.py` in your script, you can include that in the workflow by changing the `WORKFLOW_FILES` line:

```
# In Makefile
WORKFLOW_FILES = info.plist serach.py icon.png
```

### 3. Install a development version of the workflow to Alfred

Then, create a **development version** of the workflow with this command:

```sh
make install-dev
```

This action creates symbolic links in the workflow that point back to your cloned repo, and installs a workflow with those links. This means that any changes to the workflow show up in your git repo, and vice versa.

Make sure to right click the installed workflow and change the values:

![Right click the workflow in the workflow list, and then click Edit Details](readme-images/right-click-edit-details.jpg)

Any changes you make to the workflow in Alfred will apply to the [info.plist](info.plist) file in your repo for you to commit and push to GitHub. If you add any files to the workflow, update `WORKFLOW_FILES` in your Makefile again and call `make clean && make install-dev` again.

**Warning**: `make install` and `make install-dev` actions **will** replace the workflow within Alfred. If you added any files to the workflow and need to keep them, move them somewhere else (or follow the steps below for icons) **before** calling `make install` or `make install-dev`.

### 4. Add new icons to your repo

If you install new icons to workflow items, these icons get written directly to the workflow and won't get saved to your repo. This creates a problem, because they will only exist in this version of the workflow and not in a production version or new development version.

To fix this, I've written a script in [scripts/link_helper.py](scripts/link_helper.py) that looks for these icon files and moves them to your repo.

To run it, just call

```
scripts/link_helper.py
```

The script takes the following steps:

1. Finds your Alfred Preferences folder
2. Finds the workflow with the same Bundle ID
3. Checks each workflow item for a corresponding icon 
4. If the icon exists, and is not a link back to your repo, the script:
   1. Copies the file to your repo
   2. Replaces the file in the workflow with a symbolic link
   3. Updates `Makefile` to include the icon file in future workflow versions

## Deploying

The development version of the workflow **cannot** be shared with others, as it will very likely not work. It relies on all of the key files living in the same location as you have them stored on your computer.

Instead, you need to create a **production version** of the workflow:

```sh
make clean
make workflow
```

You should test that everything in your workflow still works as intended by installing this version:

```sh
make install
```

As long as you haven't changed the bundle ID, the existing version will be replaced with this version. You can then test the functionality to make sure there is no change in behavior using actual files instead of links.

Once this is done, you can take the `.alfredworkflow` file that was created and publish it on GitHub, Packal, or some other platform.