import os
import subprocess
import modal

server_timeout = 1200
modal_gpu = "t4"
invoke_port = 9090

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

@app.function(
    cpu=2,
    gpu=modal_gpu,
    memory=128,
    #keep_warm=1,
    concurrency_limit=1,
    #_allow_background_volume_commits=True,
    allow_concurrent_inputs=100,
    timeout=server_timeout,
    #enable_memory_snapshot=True,
)

@modal.web_server(port=invoke_port, startup_timeout=server_timeout)

def run_invokeai():
    invoke_start = f"""
    mkdir invokeai && wget -O invokeai/invokeai.yaml https://gist.githubusercontent.com/BarrenWardo/128c628052d8bc4bea589645bdd4732a/raw/6ecb710273b75bb92ff91d7db78ca7e01014d7fb/invokeai.yaml && invokeai-web --root invokeai
    """
    subprocess.Popen(invoke_start, shell=True)
