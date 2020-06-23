# ref : https://www.willandskill.se/en/deleting-your-git-commit-history-without-removing-repo-on-github-bitbucket/
cd /home/crouchr/PycharmProjects/learnage
rm -rf .gitgit ulimit git add .
git commit -m "Removed history"
git remote add origin github.com:crouchr/learning.git
git push -u --force origin master
