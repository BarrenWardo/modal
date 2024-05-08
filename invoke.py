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
    .run_commands(
        "mkdir invokeai",
        "wget -O https://gist.githubusercontent.com/BarrenWardo/128c628052d8bc4bea589645bdd4732a/raw/eb29b3a026dd50689059656265d54a89017cdd8f/invokeai.yaml invokeai/invokeai.yaml",
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
    invokeai-web
    """
    subprocess.Popen(invoke_start, shell=True)
