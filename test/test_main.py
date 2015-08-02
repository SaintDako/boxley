import os
import sys
import json
import dropbox
sys.path.append("../boxley")     # damn relative paths
import main as boxley


def pull_helper(id1, id2, content1, content2, cwd, cwd_without_home, client):
    # files that are not in a group
    file1_path = os.path.join(cwd, "example-files/file_%d.txt" % id1)
    file2_path = os.path.join(cwd, "example-files/file_%d.txt" % id2)
    paths = [file1_path, file2_path]

    # create the files and put them on Dropbox
    with open(file1_path, 'w') as FILE1:
        FILE1.write(content1)
    with open(file2_path, 'w') as FILE2:
        FILE2.write(content2)
    with open(file1_path, "rb") as FILE1:
        client.put_file("/Boxley/%s/example-files/file_%d.txt" % (cwd_without_home, id1),
                        FILE1, overwrite=True)
    with open(file2_path, "rb") as FILE2:
        client.put_file("/Boxley/%s/example-files/file_%d.txt" % (cwd_without_home, id2),
                        FILE2, overwrite=True)

    return paths


def test_Make_Group_File():
    boxley._Make_Group_File("example-files/group-test.conf")
    with open("example-files/group-test.conf") as TESTFILE:
        content = TESTFILE.read()

    assert content == "{}\n"


def test_Add():
    # default Dropbox directory = /Boxley
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /

    path1 = os.path.join(cwd, "example-files/file_1.txt")
    path2 = os.path.join(cwd, "example-files/file_2.txt")
    paths_to_add = [path1, path2]

    # should go to /Boxley/.../boxley/test/example-files/file_*.txt
    boxley.Add(paths_to_add, None, None, False)
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        paths = { 
            path1: "/Boxley/%s/example-files/file_1.txt" % cwd_without_home,
            path2: "/Boxley/%s/example-files/file_2.txt" % cwd_without_home
        }
        assert paths == json.loads(PATHS.read())

    # should go to /Boxley/Add-Test-1/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-1", None, False)
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        paths = {path1:"/Boxley/Add-Test-1/example-files/file_1.txt", path2:"/Boxley/Add-Test-1/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())

    # should go to /Boxley/Add-Test-2/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-2", "addtest2", False)
    with open(os.path.join(boxley_dir, "group-addtest2.conf")) as PATHS:
        paths = {path1: "/Boxley/Add-Test-2/example-files/file_1.txt", path2: "/Boxley/Add-Test-2/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())

    # should go to /Add-Test-3/example-files/file_*.txt
    boxley.Add(paths_to_add, "Add-Test-3", "addtest3", True)
    with open(os.path.join(boxley_dir, "group-addtest3.conf")) as PATHS:
        paths = {path1: "/Add-Test-3/example-files/file_1.txt", path2: "/Add-Test-3/example-files/file_2.txt"}
        assert paths == json.loads(PATHS.read())


def test_Delete():
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")
    cwd = os.getcwd()

    path1 = os.path.join(cwd, "example-files/file_1.txt")
    path2 = os.path.join(cwd, "example-files/file_2.txt")
    paths = [path1, path2]

    boxley.Add(paths, None, None, False)
    boxley.Add(paths, None, "testgroup", False)

    boxley.Delete(paths, None)
    with open(os.path.join(boxley_dir, "paths.conf")) as PATHS:
        assert "{}\n" == PATHS.read()

    boxley.Delete(paths, "testgroup")
    with open(os.path.join(boxley_dir, "group-testgroup.conf")) as PATHS:
        assert "{}\n" == PATHS.read()


def test_Make_Group():
    home = os.path.expanduser("~")
    boxley_dir = os.path.join(home, ".boxley")

    boxley.Make_Group(["groupA", "groupB"])
    assert os.path.isfile(os.path.join(boxley_dir, "group-groupA.conf")) == True
    assert os.path.isfile(os.path.join(boxley_dir, "group-groupB.conf")) == True


def test_Pull():
    # the way `Pull` is tested is by manually putting a file on Dropbox,
    # making a path to it in the *.conf files, changing the file locally,
    # pulling, and then verifying that it is the same as the Dropbox version
    home = os.path.expanduser("~")
    boxley_dir, ACCESS_TOKEN = boxley._Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /
    content1, content2 = "hello\nhello\ngoodbye!", "just-some-garbage"

    paths = pull_helper(1, 2, content1, content2, cwd, cwd_without_home, client)
    boxley.Add(paths, None, None, False)

    # edit the files, pull, check.
    with open(paths[0], 'w') as FILE1:
        FILE1.write("some random new garbage\n")
    with open(paths[1], 'w') as FILE2:
        FILE2.write("POOP: People Order Our Patties\n")
    boxley.Pull(paths, None, False)

    with open(paths[0]) as FILE1:
        assert content1 == FILE1.read()
    with open(paths[1]) as FILE2:
        assert content2 == FILE2.read()


    # files that are in a group
    content3, content4 = "I'M IN a group!!", "as\n\nam\n\ni\n"
    paths = pull_helper(3, 4, content3, content4, cwd, cwd_without_home, client)
    boxley.Add(paths, None, "pulltest", False)

    with open(paths[0], 'w') as FILE3:
        FILE3.write("ugh.\n")
    with open(paths[1], 'w') as FILE4:
        FILE4.write("Mr. Robot is awesome.\n")
    boxley.Pull(paths, "pulltest", False)

    with open(paths[0]) as FILE3:
        assert content3 == FILE3.read()
    with open(paths[1]) as FILE4:
        assert content4 == FILE4.read()

def test_Pull_Group():
    home = os.path.expanduser("~")
    boxley_dir, ACCESS_TOKEN = boxley._Get_Pull_Settings()
    client = dropbox.client.DropboxClient(ACCESS_TOKEN)
    cwd = os.getcwd()
    cwd_without_home = cwd.replace(home, "")[1:]  # remove leading /

    # files that are not in a group
    content1, content2 = "group1file1", "groupunfiledeux"
    paths = pull_helper(1, 2, content1, content2, cwd, cwd_without_home, client)
    boxley.Add(paths, None, "pullgrouptest_A", False)

    # edit the files, pull, check.
    with open(paths[0], 'w') as FILE1:
        FILE1.write("i dunno man\n")
    with open(paths[1], 'w') as FILE2:
        FILE2.write("out of ideas\n")
    boxley.Pull_Group(["pullgrouptest_A"], False)

    with open(paths[0]) as FILE1:
        assert content1 == FILE1.read()
    with open(paths[1]) as FILE2:
        assert content2 == FILE2.read()

    # files that are in a group
    content3, content4 = "groupBfileAAA", "groupBfileBBB"
    content5, content6 = "zippo", "nada!"
    paths1 = pull_helper(3, 4, content3, content4, cwd, cwd_without_home, client)
    paths2 = pull_helper(5, 6, content5, content6, cwd, cwd_without_home, client)
    boxley.Add(paths1, None, "pullgrouptest_BB", False)
    boxley.Add(paths2, None, "pullgrouptest_CCC", False)

    with open(paths1[0], 'w') as FILE3:
        FILE3.write("idea: artists\n")
    with open(paths1[1], 'w') as FILE4:
        FILE4.write("sirensceol\n")
    with open(paths2[0], 'w') as FILE5:
        FILE5.write("gibbz\n")
    with open(paths2[1], 'w') as FILE6:
        FILE6.write("free the skies\n")

    boxley.Pull_Group(["pullgrouptest_BB", "pullgrouptest_CCC"], False)

    with open(paths1[0]) as FILE3:
        assert content3 == FILE3.read()
    with open(paths1[1]) as FILE4:
        assert content4 == FILE4.read()
    with open(paths2[0]) as FILE5:
        assert content5 == FILE5.read()
    with open(paths2[1]) as FILE6:
        assert content6 == FILE6.read()