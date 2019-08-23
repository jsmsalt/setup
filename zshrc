#################
#  YARN CONFIG  #
#################

unset MANPATH
export PATH=${PATH}:$HOME/.local/bin
# YARN BIN PATH: yarn global bin
export PATH=${PATH}:$HOME/.yarn/bin
alias cra='create-react-app'

####################
#  FLUTTER CONFIG  #
####################

export PATH=${PATH}:$HOME/Keep/App/flutter/bin
# JAVA PATH: update-alternatives --query java | sed -n -e 's/Best: *\(.*\)\/bin\/java/\1/p'
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export ANDROID_HOME=$HOME/Keep/App/android-sdk
export PATH=${PATH}:$ANDROID_HOME/emulator
export PATH=${PATH}:$ANDROID_HOME/tools
export PATH=${PATH}:$ANDROID_HOME/tools/bin
export PATH=${PATH}:$ANDROID_HOME/platform-tools
alias androidemulator='emulator -avd Nexus_5X_API_29_x86'

# sudo apt install qemu-kvm
# sudo adduser $USER kvm
# sudo chown $USER -R /dev/kvm
# docker images -a | grep -v "REPOSITORY" | awk '{print $3}' | xargs -r docker rmi


######################
#  DOCKER SHORTCUTS  #
######################

# Stop docker containers
alias dstc='docker ps -a -q | xargs -r docker stop'

# Remove docker containers
alias drmc='docker ps -a -q -f status=exited | xargs -r docker rm'

# Remove docker images
alias drmi='docker images -a -q | xargs -r docker rmi'

# Remove docker volumes
alias drmv='docker volume ls -qf dangling=true | xargs -r docker volume rm'

# Docker prune
alias dprune='docker system prune -a -f --volumes'

# Stop docker web containers
alias dstwc='docker ps -a -q -f=name=nodeapp | xargs -r docker stop'

# Remove docker web containers
alias drmwc='docker ps -a -q -f=name=nodeapp -f status=exited | xargs -r docker rm'

# CLEAN
alias dclean='echo "Cleaning...";dstc;drmc;drmi;drmv;dprune'

# STOP CONTAINERS
alias dstop='echo "Stopping...";dstc;drmc'

# STOP WEB CONTAINERS
alias webstop='echo "Stopping web server...";dstwc;drmwc;drmv'

# STARTING WEB SERVER
alias webstart='webstop;echo "Starting web server..."; docker-compose up -d'

# WEB SERVER LOGS
alias weblogs='docker logs nodeapp-web'

