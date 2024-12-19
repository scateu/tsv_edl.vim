# https://stackoverflow.com/questions/12191010/git-keep-only-the-latest-version-of-a-specific-file
#
# test -e tsv_edl_refcard.pdf || exit 1
# git commit --allow-empty -a -m "updating before erasing history of tsv_edl_refcard.pdf"
# git filter-repo --path tsv_edl_refcard.pdf --invert-paths
# git remote add origin https://github.com/scateu/tsv_edl.vim.git
# git config remote.origin.url git@github.com:scateu/tsv_edl.vim.git
# cp tsv_edl_refcard.pdf docs
# git add tsv_edl_refcard.pdf
# git push --force -u origin master


# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository


# brew install git-filter-repo

mkdir _tmp_for_refcard_git_history_clean

mv tsv_edl_refcard.pdf _tmp_for_refcard_git_history_clean/
mv tsv_edl_refcard.pages _tmp_for_refcard_git_history_clean/
mv tsv_edl_flow.graffle _tmp_for_refcard_git_history_clean/
mv tsv_edl_flow.png _tmp_for_refcard_git_history_clean/

git filter-repo --force --invert-paths --path tsv_edl_refcard.pdf
git filter-repo --force --invert-paths --path tsv_edl_refcard.pages
git filter-repo --force --invert-paths --path tsv_edl_flow.graffle
git filter-repo --force --invert-paths --path tsv_edl_flow.png

mv _tmp_for_refcard_git_history_clean/* .
rmdir _tmp_for_refcard_git_history_clean

git add tsv_edl_refcard.pdf
git add tsv_edl_refcard.pages
git add tsv_edl_flow.graffle
git add tsv_edl_flow.png

git commit -m 'erase history of some large files' 

git remote add origin https://github.com/scateu/tsv_edl.vim.git
git config remote.origin.url git@github.com:scateu/tsv_edl.vim.git

git push --force -u origin main
