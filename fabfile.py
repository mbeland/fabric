from fabric.api import *
from io import StringIO


env.use_ssh_config = True
repoList = {}


def commit():
    local("git add -p && git commit")


def push():
    local("git push")


def reboot():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            sudo("shutdown -r 1", shell=False)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def apt_update():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            print("Updating system...")
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
            print("Updating system...")
            sudo("yum -y update", shell=False)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def opkg_update():
    with show('running', 'stdout', 'stderr'):
        is_done = True

        try:
            print("Updating system...")
            run("opkg update", shell=False)
            packages = run("opkg list-upgradable | awk '{print $1}' | "
                           "sed ':M;N;$!bM;s#\\n# #g'", shell=False)
            if packages:
                run("opkg upgrade %s" % packages, shell=False)
            else:
                print("No updated packages")
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
        power_sudoers = "matt * = (root) NOPASSWD: /sbin/shutdown"

        try:
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % apt_sudoers)
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % yum_sudoers)
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
                updateRepos()
            elif (sysType == "yum"):
                yum_update()
                updateRepos()
            else:
                raise ValueError("I don't recognize this machine type")
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def readRepoList(repoListFile='~/.repoList'):
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        fd = StringIO()

        try:
            get(repoListFile, fd)
            contents = fd.getvalue()
            for line in contents.splitlines():
                if line.startswith('#'):
                    next
                else:
                    newRep = line.split(':')
                    repoList[newRep[0]] = newRep[1]
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def updateRepos():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            readRepoList()
            readRepoList('~/.repoList.local')
            for key in repoList:
                remote_repo_update(key, repoList[key])
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done

def system_type():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            type = run("uname -s")
            print(str(type))
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done
