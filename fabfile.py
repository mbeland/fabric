from fabric.api import *
from os import *


env.use_ssh_config = True
scriptFileName = None
repoList = {}


def get_immediate_subdirectories(a_dir='~/repos/'):
    result = run("find %s -maxdepth 1 -type d" % a_dir)
    result = result.splitlines()
    del result[0]
    return result


@serial
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
            sudo("DEBIAN_FRONTEND=noninteractive apt upgrade -yq", shell=False,
                 timeout=120)
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
                if '.postpull.sh' in pathList.stdout:
                    print("%s - updating permissions" % repoName)
                    run('./.postpull.sh')
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def setup():
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        apt_sudoers = "matt * = (root) NOPASSWD:SETENV: /usr/bin/apt"
        power_sudoers = "matt * = (root) NOPASSWD: /sbin/shutdown"

        try:
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % apt_sudoers)
            sudo("echo \"%s\" >> /etc/sudoers.d/fabric" % power_sudoers)
            pathList = run('ls -a ~')
            if "repos" not in pathList.stdout:
                print("No repos dir - creating")
                run("mkdir ~/repos/")
            if "bin" not in pathList.stdout:
                print("No bin dir - cloning")
                run("git clone https://github.com/mbeland/bin.git")
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


@parallel
def updates():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            apt_update()
            updateRepos()
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
            repo_update("Home Bin", "~/bin/")
            repo_update("SSH", "~/.ssh")
            repo_update("Home Dir", "~/")
            dirsToUpdate = get_immediate_subdirectories(reposDir)
            for x in dirsToUpdate:
                y = x.split("/")
                repo_update(y[-1], x)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done


def deploy_script():
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        global scriptFileName

        try:
            if scriptFileName:
                scriptFileName = input('Script to execute: ')
            put(scriptFileName, "/tmp/", mirror_local_mode=True)
            remotePath = "/tmp/" + scriptFileName
            run(remotePath)
            run("rm " + remotePath)
        except Exception as e:
            print(str(e))
            is_done = False
        finally:
            return is_done
