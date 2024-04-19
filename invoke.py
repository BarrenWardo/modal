import os
import subprocess
import modal

from modal import web_server

server_timeout = 600
modal_gpu = "t4"
vol_dir = "/root/invokeai"
invoke_port = 9090

stub = modal.Stub(
    image=modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "libgl1-mesa-glx",
        "build-essential",
        "python3-opencv",
        "libopencv-dev",
    )  
    .pip_install(
        "pypatchmatch",
        "InvokeAI[xformers]" --use-pep517 --extra-index-url https://download.pytorch.org/whl/cu121,
    )
)

volume = modal.Volume.from_name(
    "invokeai", create_if_missing=True
)

@stub.function(
    cpu=4,
    gpu=modal_gpu,
    memory=256,
    keep_warm=1,
    concurrency_limit=1,
    volumes={vol_dir: volume},
    _allow_background_volume_commits=True,
)

@web_server(port=invoke_port, startup_timeout=server_timeout)

def run_invokeai():
    invoke_start = f"""
    cd {vol_dir} && invokeai-web --root {vol_dir}
    """
    subprocess.Popen(invoke_start, shell=True)