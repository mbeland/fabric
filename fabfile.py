from fabric.api import *


env.use_ssh_config = True


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


def test_remote():
    run('uname -n')
