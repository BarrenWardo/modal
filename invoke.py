import os
import subprocess
import modal

server_timeout = 1200
modal_gpu = "t4"
DIR = "/root/invokeai"

app = modal.App(
    "InvokeAI",
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
        "InvokeAI[xformers]",
        extra_index_url="https://download.pytorch.org/whl/cu121",
    )
)

volume = modal.Volume.from_name(
    "invokeai", create_if_missing=True)

@app.function(
    cpu=2,
    gpu=modal_gpu,
    memory=128,
    #keep_warm=1,
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    timeout=server_timeout,
    #enable_memory_snapshot=True,
    volumes={DIR: volume},
    _allow_background_volume_commits=True,
)

@modal.web_server(9090,startup_timeout=server_timeout)

def run_invokeai():
    invoke_start = f"""
    invokeai-web --root {DIR} --config {DIR}/invokeai.yaml
    """
    subprocess.Popen(invoke_start, shell=True)
