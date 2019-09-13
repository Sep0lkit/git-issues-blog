#install jq
sudo apt-get -y install jq

#changed file list
commit=`cat _index | jq -r  .__commit__`
echo $commit
if [ -n "$commit" ]; then
	echo "output git changed file list..."
	git config --global core.quotepath false
    git diff --name-only $commit  > git_diff_files.txt
else
	echo "no commit found, changed set to null"
    echo '' > git_diff_files.txt
fi
