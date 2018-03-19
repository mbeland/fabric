from fabric.api import *
import os
from io import StringIO, BytesIO


env.use_ssh_config = True
repoList = {}


def get_immediate_subdirectories(a_dir='~/repos/'):
    result = run("find %s -maxdepth 1 -type d" % a_dir)
    result = result.splitlines()
    del result[0]
    return result


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
            sudo("DEBIAN_FRONTEND=noninteractive apt -yq upgrade", shell=False)
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
                pathList = run('ls -a')
                if ".noPull" in pathList.stdout:
                    print("%s has .noPull - skipping" % repoName)
                    return is_done
                r = run('git pull')
                if 'Already up-to-date' in r.stdout:
                    print("%s already up-to-date" % repoName)
                else:
                    print("%s updated" % repoName)
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
        apt_sudoers = "matt * = (root) NOPASSWD:SETENV: /usr/bin/apt"
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


def readRepoList():
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        fd = BytesIO()

        try:
            get('~/.repoList', fd)
            contents = fd.getvalue().splitlines()
            for line in contents:
                line = line.decode()
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
        reposDir = '~/repos/'

        try:
            readRepoList()
            for key in repoList:
                repo_update(key, repoList[key])
            dirsToUpdate = get_immediate_subdirectories(reposDir)
            for x in dirsToUpdate:
                y = x.split("/")
                repo_update(y[-1], x)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done
