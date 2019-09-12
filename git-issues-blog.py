#!/usr/bin/env python3
''' Create Issue From File '''
import os
import re
import json
import pathlib
import requests
import subprocess
from github import Github

GITHUB_API = "https://api.github.com"
GITHUB_ACTION_NAME = os.environ['GITHUB_ACTION']

# Get environment variables
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'master')
POSTS_PATH = os.getenv('POSTS_PATH', 'posts')
POSTS_INDEX = os.getenv('POSTS_INDEX', '_index')
# Global variables
POSTS = []
CHANGED = []

# github object
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

# local dictionary
dictionary = {}
index = pathlib.Path(POSTS_INDEX)
if index.exists():
    try:
        with open(POSTS_INDEX, encoding='utf-8', mode = 'r') as fp:
            dictionary = json.load(fp)
        lastcommit = dictionary['__commit__']
        command = "git diff --name-only " + lastcommit
        changed = subprocess.check_output(command).decode()
        CHANGED = [y for y in (x.strip() for x in changed.splitlines()) if y]
    except:
        print('%s load error' % POSTS_INDEX)
        exit(-1)

print("changed file: ")
print(CHANGED)

p = pathlib.Path(POSTS_PATH)
for f in p.rglob('*.md'):
    if len(CHANGED) != 0:
        if (f.as_posix() in CHANGED): 
            print("post %s need update" % f.as_posix())          
            POSTS.append(f)
    else:
        POSTS.append(f)

header = pathlib.Path('_tpl/post-header.md')
if header.exists():
    issue_header = header.read_text()
else:
    issue_header = ""

footer = pathlib.Path('_tpl/post-footer.md')
if footer.exists():
    issue_footer = footer.read_text()
else:
    issue_footer = ""


for p in POSTS:
    # issue content templat)e
    with open(p, encoding='utf-8', mode = 'r') as f:
        issue_body = f.read()

        # relative link to raw.github link
        re_format = "![\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(GITHUB_REPO, GITHUB_BRANCH, p.parent.as_posix())
        issue_body_new = re.sub(r'!\[(.*)\]\((?!http)(.*)\)', re_format, issue_body, flags = re.M)

    issue_content = issue_header + issue_body_new + issue_footer

    # check file exist issue or not by title(POSTS_PATH)
    pstr = p.as_posix()
    if pstr in dictionary: 
        # get issue info
        issue_number = dictionary[pstr]
        issue = repo.get_issue(number=issue_number)
        issue_url = issue.html_url
        issue_title = issue.title

        # content
        payload = {}
        payload['title'] = issue_title
        payload['body'] = issue_content

        # github edit issue api
        header = {'Authorization': 'token %s' % GITHUB_TOKEN}

        url = GITHUB_API + "/repos/" + GITHUB_REPO + "/issues/" + str(issue_number)
        r = requests.patch(url, headers=header, data=json.dumps(payload))
        if r.status_code == 200:
            print("issue update successful: %s" % issue_number)
        else:
            print("issue update failed: %s" % issue_number)
            exit(-1)

    else:
        #creat issue
        title = p.name
        issue = repo.create_issue(title, issue_content)
        print("issue create successfule: %s" % issue.number)
        dictionary[pstr] = issue.number

commit = os.environ['GITHUB_SHA']
print("update posts to commit id: %s" % commit)
if re.search("^\w{40}$", commit):
    dictionary['__commit__'] = commit
else:
    print('last commit id got error')
    exit(-1)

#write posts index and commit step
#update POSTS_INDEX
post_index_content = json.dumps(dictionary)
post_index_file = repo.get_contents(POSTS_INDEX,ref=GITHUB_BRANCH)
post_index_msg = "rebuild posts index from: " + GITHUB_ACTION_NAME
repo.update_file(post_index_file.path, post_index_msg, post_index_content, post_index_file.sha, branch=GITHUB_BRANCH)

print("posts update successful")
