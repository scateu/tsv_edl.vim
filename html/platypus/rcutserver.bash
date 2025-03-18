export LANG=en_US.UTF-8; export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin/; 
cp rcut2.html "$1"/index.html
RESOURCE_PWD="$(pwd)"
echo APP RESOURCE PATH: "${RESOURCE_PWD}"
cd "$1"
echo "http://github.com/scateu/tsv_edl.vim"
echo "===================================="
echo "     Starting rCut Server           "
                                  
"${RESOURCE_PWD}"/rcutserver-mac-arm64 -d "$1" -p 80 -l 0.0.0.0 -s "${RESOURCE_PWD}"/tsv2roughcut.py
