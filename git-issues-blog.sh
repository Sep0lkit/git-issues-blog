# Author: Sep0lkit
# Github: https://github.com/Sep0lkit/git-issues-blog

# install jq
sudo apt-get -y install jq

# changed file list
commit=`cat _index | jq -r  .__commit__`
echo $commit
if [ -n "$commit" ]; then
	git config --global core.quotepath false
    git diff --name-only $commit  > git_diff_files.txt
	echo "posts will be update: "
	cat git_diff_files.txt
else
	echo "no commit found, all posts will be update: "
    echo '' > git_diff_files.txt
fi
