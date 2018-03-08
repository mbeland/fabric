from fabric.api import *
import os
from io import StringIO


env.use_ssh_config = True
repoList = {}


def get_immediate_subdirectories(a_dir='~/repos/'):
    a_dir = os.path.expanduser(a_dir)
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


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


def repo_update(repoName="Home Bin", repoDirectory="~/bin/"):
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


def setup():
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
    with show('running', 'stdout', 'stderr'):
        is_done = True

        try:
            contents = run("cat %s" % repoListFile)
            for line in contents:
                print(line)
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
        reposPath = '~/repos/'

        try:
            readRepoList()
            for key in repoList:
                repo_update(key, repoList[key])
            for reposDir in get_immediate_subdirectories(reposPath):
                reposDir = reposPath + repoDir
                repo_update(reposDir, reposDir)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done
