import os
import subprocess
import sys

def is_str_in_list(given_str, list_str):
    if given_str not in list_str:
        print(f"{given_str} is not supported!")
        sys.exit(1)

tasks = ["test", "build", "push"]
t = input("Task ({}): ".format('|'.join(tasks))) if len(sys.argv) < 2 else sys.argv[1]
is_str_in_list(t, tasks)

projects = ["base", "emulator", "genymotion", "pro-emulator", "pro-emulator_headless"]
p = input("Project ({}): ".format('|'.join(projects))) if len(sys.argv) < 3 else sys.argv[2]
is_str_in_list(p, projects)

r_v = input("Release Version (v2.0.0-p0|v2.0.0-p1|etc): ") if len(sys.argv) < 4 else sys.argv[3]

FOLDER_PATH = ""
IMAGE_NAME = ""
TAG_NAME = ""

if "pro" in p:
    arr = p.split('-')
    FOLDER_PATH += f"docker/{arr[0]}/{arr[1]}"
    IMAGE_NAME += f"budtmo2/docker-android-{arr[0]}"
    TAG_NAME += f"{arr[1]}"
else:
    FOLDER_PATH += f"docker/{p}"
    IMAGE_NAME += "budtmo/docker-android"
    TAG_NAME += f"{p}"

a_v = None
if "emulator" in p:
    supported_android_version = ["9.0", "10.0", "11.0", "12.0", "13.0", "14.0"]
    api_levels = {
        "9.0": 28,
        "10.0": 29,
        "11.0": 30,
        "12.0": 32,
        "13.0": 33,
        "14.0": 34
    }

    sorted_keys = sorted(api_levels.keys())
    last_key = sorted_keys[-2]

    a_v = input("Android Version ({}): ".format('|'.join(supported_android_version))) if len(sys.argv) < 5 else sys.argv[4]
    is_str_in_list(a_v, supported_android_version)
    a_l = api_levels[a_v]
    TAG_NAME += f"_{a_v}"

IMAGE_NAME_LATEST = f"{IMAGE_NAME}:{TAG_NAME}"
TAG_NAME += f"_{r_v}"
IMAGE_NAME_SPECIFIC_RELEASE = f"{IMAGE_NAME}:{TAG_NAME}"
print(f"{IMAGE_NAME_SPECIFIC_RELEASE} or {IMAGE_NAME_LATEST}")

def build():
    cmd = f"docker build -t {IMAGE_NAME_SPECIFIC_RELEASE} --build-arg DOCKER_ANDROID_VERSION={r_v} "
    if a_v:
        cmd += f"--build-arg EMULATOR_ANDROID_VERSION={a_v} --build-arg EMULATOR_API_LEVEL={a_l} "
    cmd += f"-f {FOLDER_PATH} ."
    os.system(cmd)
    os.system(f"docker tag {IMAGE_NAME_SPECIFIC_RELEASE} {IMAGE_NAME_LATEST}")
    if a_v and a_v == last_key:
        print(f"{a_v} is the last version in the list, will use it as default image tag")
        os.system(f"docker tag {IMAGE_NAME_SPECIFIC_RELEASE} {IMAGE_NAME}:latest")

def test():
    cli_path = "/home/androidusr/docker-android/cli"
    results_path = "test-results"
    tmp_folder = "tmp"

    os.makedirs(tmp_folder, exist_ok=True)
    build()
    os.system(f"docker run -it --rm --name test --entrypoint /bin/bash \
    -v $PWD/{tmp_folder}:{cli_path}/{tmp_folder} {IMAGE_NAME_SPECIFIC_RELEASE} \
    -c 'cd {cli_path} && sudo rm -rf {tmp_folder}/* && \
    nosetests -v && sudo mv .coverage {tmp_folder} && \
    sudo cp -r {results_path}/* {tmp_folder} && sudo chown -R 1300:1301 {tmp_folder} &&\
    sudo chmod a+x -R {tmp_folder}'")

def push():
    build()
    os.system(f"docker push {IMAGE_NAME_SPECIFIC_RELEASE}")
    os.system(f"docker push {IMAGE_NAME_LATEST}")
    if a_v and a_v == last_key:
        os.system(f"docker push {IMAGE_NAME}:latest")

if t == "build":
    build()
elif t == "test":
    test()
elif t == "push":
    push()
