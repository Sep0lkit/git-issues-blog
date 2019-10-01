#!/usr/bin/env python3

# Author: Sep0lkit
# Github: https://github.com/Sep0lkit/git-issues-blo

import os
import re
import json
import pathlib
import requests
import subprocess
import urllib.parse
from github import Github
from github import GithubException
from github import UnknownObjectException

GITHUB_API = "https://api.github.com"
GITHUB_ACTION_NAME = os.environ['GITHUB_ACTION']

# Get environment variables
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
GITHUB_USER = GITHUB_REPO.split('/')[0]
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'master')
POSTS_PATH = os.getenv('POSTS_PATH', 'posts')
POST_INDEX_FILE = os.getenv('POST_INDEX_FILE', '_index')
# Global variables
POSTS = []
CHANGED = []


# github object
g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

# local dictionary
dictionary = {}
index = pathlib.Path(POST_INDEX_FILE)
if index.exists():
    try:
        with open(POST_INDEX_FILE, encoding='utf-8', mode = 'r') as f:
            dictionary = json.load(f)
        lastcommit = dictionary['__commit__']
        command = "git diff --name-only -z " + lastcommit
        changed = subprocess.check_output(['git', 'diff', '--name-only', '-z', lastcommit])
        for x in changed.split(b'\x00'):
            if x.decode('utf-8'):
                CHANGED.append(x.decode('utf-8'))
        f.close()
    except Exception as e:
        print('%s load error: %s' % (POST_INDEX_FILE, e))
        exit(-1)


p = pathlib.Path(POSTS_PATH)
for f in p.rglob('*.md'):
    if len(CHANGED) != 0:
        if (f.as_posix() in CHANGED): 
            print("post %s need update" % f.as_posix())          
            POSTS.append(f)
    else:
        POSTS.append(f)

print("posts need update: ")
print(POSTS)

header = pathlib.Path('_tpl/post-header.md')
if header.exists():
    issue_header = header.read_text()
else:
    issue_header = ""

footer = pathlib.Path('_tpl/post-footer.md')
if footer.exists():
    issue_footer = footer.read_text()
else:
    issue_footer = "\n\nPowered by [Git-Issues-Blog](https://github.com/marketplace/actions/git-issues-blog)"

# issues tpl variables function
def parse_issue_tpl(content, user, path):
    #GITHUB_POSTS_USER
    content = re.sub(r'{{\s?GITHUB_POSTS_USER\s?}}', user , content, flags=re.M)
    #GITHUB_POSTS_FILENAME
    postname = path.rsplit('/',1)[1]
    content = re.sub(r'{{\s?GITHUB_POSTS_NAME\s?}}', postname , content, flags=re.M)
    #GITHUB_POSTS_URL
    url = "https://github.com/{}/blob/{}/{}".format(GITHUB_REPO, GITHUB_BRANCH, urllib.parse.quote(path))
    content = re.sub(r'{{\s?GITHUB_POSTS_URL\s?}}', url , content, flags=re.M)

    return content

for p in POSTS:
    # issue content templat)e
    with open(p, encoding='utf-8', mode = 'r') as f:
        issue_body = f.read()
        f.close()

        # relative link to raw.github link
        re_format = "![\\1](https://raw.githubusercontent.com/{}/{}/{}/\\2)".format(GITHUB_REPO, GITHUB_BRANCH, p.parent.as_posix())
        issue_body_with_giturl = re.sub(r'!\[(.*)\]\((?!http)(.*)\)', re_format, issue_body, flags = re.M)

    # template variables in header and footer
    issue_header_with_tpl = parse_issue_tpl(issue_header, GITHUB_USER, p.as_posix())
    issue_footer_with_tpl = parse_issue_tpl(issue_footer, GITHUB_USER, p.as_posix())
    
    issue_content = issue_header_with_tpl + issue_body_with_giturl + issue_footer_with_tpl

    # check file exist issue or not by title(POSTS_PATH)
    pstr = p.as_posix()
    if pstr in dictionary: 
        # get issue info
        issue_number = dictionary[pstr]
        try:
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
        except GithubException as e:
            print('get issues: %s error, skip for next' % issue_number)

    else:
        #creat issue
        title = p.name
        title = re.sub('.md$', '', title, flags=re.IGNORECASE)
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
try:
    repo.get_contents(POST_INDEX_FILE,ref=GITHUB_BRANCH)
except UnknownObjectException:
    repo.create_file(POST_INDEX_FILE, "add post index: _index", "{}", branch=GITHUB_BRANCH)
#update POST_INDEX_FILE
post_index_file = repo.get_contents(POST_INDEX_FILE,ref=GITHUB_BRANCH)
post_index_content = json.dumps(dictionary, ensure_ascii=False)
post_index_msg = "rebuild posts index from: " + GITHUB_ACTION_NAME
repo.update_file(post_index_file.path, post_index_msg, post_index_content, post_index_file.sha, branch=GITHUB_BRANCH)

print("posts update successful")
