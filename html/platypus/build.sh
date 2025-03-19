platypus -P rcutserver.platypus -n 'Menlo 14' ./rcutserver.bash -a rcutserver -I org.scateu.rcutserver
mv rcutserver.bash.app rcutserver.app

codesign -s 8J69FR3DR8  ./rcutserver.app

zip rcutserver-mac-arm64-GUI-signed.zip rcutserver.app
