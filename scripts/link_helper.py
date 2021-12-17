#!/usr/bin/env python3

"""Helps to find new files in an Alfred workflow, and move them to this repository."""

import os
import subprocess
import logging
import json
from xml.etree import ElementTree

logger = logging.getLogger("link_helper")


def main():
    """The main logic of the program"""
    repo_root = get_repo_root()
    logger.debug("Repo at: %s", repo_root)
    bundle_id = get_bundle_id(os.path.join(repo_root, "info.plist"))
    logger.debug("Bundle ID: %s", bundle_id)
    
    try:
        workflow_path = find_workflow_path(bundle_id)
    except:
        logger.error("Could not find workflow with bundle ID '%s'.", bundle_id, exc_info=True)
        exit(1)
    logger.info("Looking for files in Workflow path %s", workflow_path)
    for new_file in scan_workflow(workflow_path):
        logger.info("Linking file %s", new_file)
        link_from_repo(new_file, repo_root)


def get_repo_root():
    """Gets the root of the git repository. 
    
    This allows the script to work regardless of the current working directory (as long as the current working directory 
    is *somewhere* in the repository in question).
    
    Returns
    -------
    str
        The path to the current repository"""
    output = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE)
    assert output.returncode == 0
    return output.stdout.decode().strip()


def get_bundle_id(info_plist_path: str):
    """Gets an Alfred workflow's bundle ID from its info.plist file
    
    Parameters
    ----------
    info_plist_path : str (path-like)
        The path to the workflow's info.plist file

    Returns
    -------
    str
        The Bundle ID (as entered in Alfred)
    """
    plist_dict = ElementTree.parse(info_plist_path).find('dict')
    bundle_id_val = get_plist_value_for_key(plist_dict, 'bundleid')
    return bundle_id_val.text


def find_workflow_path(target_bundle_id: str):
    """Finds a workflow's path based on its bundle ID
    
    Parameters
    ----------
    target_bundle_id: str
        The Bundle ID of the workflow, as it is entered into Alfred
        
    Returns
    -------
    str
        The absolute path of the first workflow found in Alfred's installed workflows that has this bundle ID.
    """
    workflow_dir = find_workflow_dir()
    logger.debug("Looking for workflow in path %s", workflow_dir)
    for workflow in os.listdir(workflow_dir):
        logger.debug("Checking %s", workflow)
        workflow_plist_path = os.path.join(workflow_dir, workflow, "info.plist")
        workflow_bundle_id = get_bundle_id(workflow_plist_path)
        if workflow_bundle_id == target_bundle_id:
            return os.path.join(workflow_dir, workflow)
    raise ValueError("Bundle ID %s not found", target_bundle_id)


def find_workflow_dir():
    """Finds the installation path for Alfred workflows"""
    alfred_prefs_path = os.path.join(os.path.expanduser('~'), "Library", "Application Support", "Alfred", "prefs.json")
    with open(alfred_prefs_path, 'r') as f:
        alfred_prefs = json.load(f)
    return os.path.join(alfred_prefs['current'], 'workflows')


def scan_workflow(workflow_dir: str):
    """Scans a workflow for files referenced in the workflow that are not symbolic links
    
    Parameters
    ----------
    workflow_dir : str
        The path to the workflow, as installed in Alfred

    Yields
    ------
    str
        The path to any new file that needs to be linked
    """
    info_plist_path = os.path.join(workflow_dir, "info.plist")
    plist_dict = ElementTree.parse(info_plist_path).find('./dict')
    objects_array = get_plist_value_for_key(plist_dict, 'objects')
    for object_dict in objects_array:
        uid = get_plist_value_for_key(object_dict, 'uid').text
        logger.debug("Checking for UID %s", uid)
        file_path = os.path.join(workflow_dir, uid + ".png")
        if os.path.exists(file_path) and not os.path.islink(file_path):
            yield file_path


def link_from_repo(file_path: str, repo_root: str):
    """Copies a file to `repo_root` and replaces the existing file with a link to the file in the repo"""
    workflow_root, file_name = os.path.split(file_path)
    assert (
        not subprocess.run(["cp", "-f", file_path, repo_root]).returncode and
        not subprocess.run(["rm", file_path]).returncode and
        not subprocess.run(["ln", "-s", os.path.join(repo_root, file_name), workflow_root]).returncode
    )
    with open(os.path.join(repo_root, 'Makefile'), 'r') as makefile_old, open(os.path.join(repo_root, 'Makefile.new'), 'w') as makefile_new:
        for line in makefile_old:
            if line.startswith("WORKFLOW_FILES ="):
                makefile_new.write(line.strip() + " " + file_name + "\n")
            else:
                makefile_new.write(line)
    assert (
        not subprocess.run(['mv', os.path.join(repo_root, 'Makefile'), os.path.join(repo_root, 'Makefile.old')]).returncode and
        not subprocess.run(['mv', os.path.join(repo_root, 'Makefile.new'), os.path.join(repo_root, 'Makefile')]).returncode and
        not subprocess.run(['rm', os.path.join(repo_root, 'Makefile.old')]).returncode
    )


def get_plist_value_for_key(plist_dict: ElementTree.Element, key: str):
    """Gets the value from a plist dictionary by its key
    
    Parameters
    ----------
    plist_dict : xml.etree.ElementTree.Element
        The `<dict>...</dict>` element to search.
    
    key : str
        The key of the element you would like to get.

    Returns
    -------
    xml.etree.ElementTree.Element or None
        The value from the plist dict, if one was found.
    """
    key_ix = None
    for i in range(0, len(plist_dict), 2):
        assert plist_dict[i].tag == 'key'
        if plist_dict[i].text == key:
            key_ix = i // 2
            break
    if key_ix is None: 
        return None
    return plist_dict[(key_ix * 2) + 1]



if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    logging.basicConfig(format="%(message)s")
    main()
