from fabric.api import *


env.use_ssh_config = True


def commit():
    local("git add -p && git commit")


def push():
    local("git push")


def reboot():
    with show('running', 'stdout', 'stderr'):
        is_done = True

        try:
            sudo("shutdown -r now", shell=False)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def apt_update():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            sudo("apt update", shell=False)
            sudo("apt -y upgrade", shell=False)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def yum_update():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            sudo("yum -y update", shell=False)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def local_repo_update(repoName="Home Bin", repoDirectory="~/bin/"):
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            with lcd(repoDirectory):
                r = local('git pull', capture=True)
                if 'Already up-to-date' in r.stdout:
                    print("%s already up-to-date" % repoName)
                else:
                    print("%s updated" % repoName)
                pathList = local('ls', capture=True)
                if 'permset.sh' in pathList.stdout:
                    print("%s - updating permissions" % repoName)
                    local('./permset.sh')
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def remote_repo_update(repoName="Home Bin", repoDirectory="~/bin/"):
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            with cd(repoDirectory):
                r = run('git pull')
                if 'Already up-to-date' in r.stdout:
                    print("%s already up-to-date" % repoName)
                else:
                    print("%s updated" % repoName)
                pathList = run('ls')
                if 'permset.sh' in pathList.stdout:
                    print("%s - updating permissions" % repoName)
                    run('./permset.sh')
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def remote_setup():
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        apt_sudoers = "matt * = (root) NOPASSWD: /usr/bin/apt"
        yum_sudoers = "matt * = (root) NOPASSWD: /usr/bin/yum"
        power_sudoers = "matt * = (root) NOPASSWD: /sbin/reboot"

        try:
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % apt_sudoers)
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % yum_sudoers)
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % power_sudoers)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def remote_setup_patch():
    with show('running', 'stdout', 'stderr'):
        is_done = True
        power_sudoers = "matt * = (root) NOPASSWD: /sbin/reboot"

        try:
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % power_sudoers)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def updates():
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        sysType = run("[[ -e /usr/bin/apt ]] && echo 'apt' || echo 'yum'")

        try:
            if (sysType == "apt"):
                apt_update()
            elif (sysType == "yum"):
                yum_update()
            else:
                raise ValueError("I don't recognize this machine type")
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done
