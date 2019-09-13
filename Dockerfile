FROM python:3.7.3

LABEL author="Sep0lkit <sep0lkit@gmail.com>"
LABEL repository="https://github.com/Sep0lkit/git-issues-blog"

LABEL com.github.actions.name="git-issues-blog"
LABEL com.github.actions.description="Auto build issues blog from github repo"
LABEL com.github.actions.icon="file-text"
LABEL com.github.actions.color="blue"

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

COPY git-issues-blog.py /git-issues-blog.py
COPY git_diff_files.txt /git_diff_files.txt
RUN chmod +x /git-issues-blog.py
ENTRYPOINT [ "/git-issues-blog.py" ]
