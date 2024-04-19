import os
import subprocess
import modal

server_timeout = 600
modal_gpu = "t4"
DIR = "/root/invokeai"

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
        "xformers",
        "torch", 
        "torchvision", 
        "torchaudio",
        "InvokeAI",
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
    volumes={DIR: volume},
    _allow_background_volume_commits=True,
)

@modal.web_server(port=9090, startup_timeout=server_timeout)

def run_invokeai():
    invoke_start = f"""
    cd {DIR} && invokeai-web --root {DIR}
    """
    subprocess.Popen(invoke_start, shell=True)