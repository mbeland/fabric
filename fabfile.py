from fabric.api import *
from os import *


env.use_ssh_config = True
env.output_prefix = True
scriptFileName = None
repoList = {}


def get_immediate_subdirectories(a_dir='~/repos/'):
    result = run("find {} -maxdepth 1 -type d".format(a_dir))
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
            print("{0} - {1}".format(env.host_string, e))
            is_done = False
        finally:
            return is_done


def apt_update():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            print("Updating {} with apt...".format(env.host_string))
            sudo("apt update", shell=False)
            sudo("DEBIAN_FRONTEND=noninteractive apt upgrade -yq", shell=False,
                 timeout=120)
            sudo("apt autoremove -yq", shell=False, timeout=120)
        except Exception as e:
            print("{0} - {1}".format(env.host_string, e))
            is_done = False
        finally:
            return is_done


def yum_update():
    with hide('running', 'stdout', 'stderr'):
        is_done = True

        try:
            print("Updating {} with yum...".format(env.host_string))
            sudo("yum -y update", shell=False)
        except Exception as e:
            print("{0} - {1}".format(env.host_string, e))
            is_done = False
        finally:
            return is_done


def opkg_update():
    with show('running', 'stdout', 'stderr'):
        is_done = True

        try:
            print("Updating {} with opkg...".format(env.host_string))
            run("opkg update", shell=False)
            packages = run("opkg list-upgradable | awk '{print $1}' | "
                           "sed ':M;N;$!bM;s#\\n# #g'", shell=False)
            if packages:
                run("opkg upgrade %s" % packages, shell=False)
            else:
                print("No updated packages on {}".format(env.host_string))
        except Exception as e:
            print("{0} - {1}".format(env.host_string, e))
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
                    print("{} repo {} has .noPull - skipping".format(env.host_string, repoName))
                    return is_done
                r = run('git pull')
                if 'Already up-to-date' in r.stdout:
                    print("{} repo {} already up-to-date".format(env.host_string, repoName))
                else:
                    print("{} repo {} updated".format(env.host_string, repoName))
                if '.postpull.sh' in pathList.stdout:
                    print("{} repo {} - updating permissions".format(env.host_string, repoName))
                    run('./.postpull.sh')
        except Exception as e:
            print("{0} - {1}".format(env.host_string, e))
            is_done = False
        finally:
            return is_done


def setup():
    with hide('running', 'stdout', 'stderr'):
        is_done = True
        apt_sudoers = "matt * = (root) NOPASSWD:SETENV: /usr/bin/apt,"\
            "/usr/local/bin/apt"
        power_sudoers = "matt * = (root) NOPASSWD: /sbin/shutdown"

        try:
            sudo("echo \"{}\" >> /etc/sudoers.d/fabric".format(apt_sudoers))
            sudo("echo \"{}\" >> /etc/sudoers.d/fabric".format(power_sudoers))
            pathList = run('ls -a ~')
            if "repos" not in pathList.stdout:
                print("No repos dir on {} - creating".format(env.host_string))
                run("mkdir ~/repos/")
            if "bin" not in pathList.stdout:
                print("No bin dir on {} - cloning".format(env.host_string))
                run("git clone https://github.com/mbeland/bin.git")
        except Exception as e:
            print("{0} - {1}".format(env.host_string, e))
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
            print("{0} - {1}".format(env.host_string, e))
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
            print("{0} - {1}".format(env.host_string, e))
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
            print("{0} - {1}".format(env.host_string, e))
            is_done = False
        finally:
            return is_done
