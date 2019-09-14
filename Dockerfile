FROM alpine:3.7

LABEL author="Sep0lkit <sep0lkit@gmail.com>"
LABEL repository="https://github.com/Sep0lkit/git-issues-blog"

# Github action labels
LABEL com.github.actions.name="git-issues-blog"
LABEL com.github.actions.author="Sep0lkit"
LABEL com.github.actions.description="Auto build issues blog from github repo"
LABEL com.github.actions.icon="file-text"
LABEL com.github.actions.color="blue"

# Install packages
RUN apk add --no-cache bash git jq
RUN apk add --no-cache python3 && python3 -m ensurepip && pip3 --no-cache-dir install --upgrade pip
RUN pip3 install requests PyGithub pathlib


COPY git-issues-blog.py /git-issues-blog.py
RUN chmod +x /git-issues-blog.py
ENTRYPOINT [ "/git-issues-blog.py" ]
