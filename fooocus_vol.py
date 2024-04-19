# In your local system terminal install modal using "pip install modal"
# Setup modal by creating API token then copy paste it in terminal. It should look something like this "modal token set --token-id TOKEN_ID --token-secret TOKEN_SECRET"
# Create a modal volume using "modal volume create fooocus"
# Clone fooocus using "git clone https://github.com/lllyasviel/Fooocus.git"
# Create a modal volume for fooocus by running "modal volume create fooocus"
# Add Fooocus to volume using "modal volume put fooocus Fooocus"
# It's ready now. You can deploy Fooocus using "modal deploy fooocus_vol.py --name fooocus"
# You can also run it temporarily using "modal serve fooocus_vol.py --timeout 3600" (3600 = 3600 secs = 1 hr)


import os
import subprocess
import modal

from modal import web_server

fooocus_port = 7860
server_timeout = 600
modal_gpu = "t4"
DIR = "/root/fooocus"

stub = modal.Stub(
    image=modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )  
)

volume = modal.Volume.from_name(
    "fooocus"
)

@stub.function(
        cpu=2,
        gpu=modal_gpu,
        memory=128,
        keep_warm=1,
        concurrency_limit=1,
        volumes={DIR: volume},
        _allow_background_volume_commits=True,
)

@web_server(port=fooocus_port, startup_timeout=server_timeout)

def run_fooocus():
    fooocus_process = f"""
    cd {DIR} && cd Fooocus && git pull && pip install -r requirements_versions.txt && python entry_with_update.py --listen --port {fooocus_port}
    """
    subprocess.Popen(fooocus_process, shell=True)
