import os
import subprocess

import modal

stub = modal.Stub(
    image=modal.Image.debian_slim().pip_install(
        "jupyter",
    )
)
nfs = modal.NetworkFileSystem.from_name(
    "sd", create_if_missing=True
)

CACHE_DIR = "/root/SD"
# Define the name of the secret containing the Jupyter token
JUPYTER_TOKEN_SECRET_NAME = "JLT"

# Define GPU configurations
GPU = "None"

# Define timeout
TIMEOUT = 3600  # Timeout set to 1 hour (3600 seconds)

# Function to get GPU configuration
def get_gpu_config(gpu_name):
    if gpu_name == "t4":
        return modal.gpu.T4()
    elif gpu_name == "l4":
        return modal.gpu.L4()
    elif gpu_name == "a100":
        return modal.gpu.A100()
    elif gpu_name == "h100":
        return modal.gpu.H100()
    elif gpu_name == "a10g":
        return modal.gpu.A10G()
    elif gpu_name == "any":
        return modal.gpu.Any()
    else:
        return None

@stub.function(network_file_systems={CACHE_DIR: nfs})
def seed_volume():
    pass


@stub.function(concurrency_limit=1, network_file_systems={CACHE_DIR: nfs}, gpu=get_gpu_config(GPU) if GPU else None, timeout=TIMEOUT, secrets=[modal.Secret.from_name(JUPYTER_TOKEN_SECRET_NAME)])
def run_jupyter():
    jupyter_port = 8888
    with modal.forward(jupyter_port) as tunnel:
        jupyter_process = subprocess.Popen(
            [
                "jupyter",
                "notebook",
                "--no-browser",
                "--allow-root",
                "--ip=0.0.0.0",
                f"--port={jupyter_port}",
                "--NotebookApp.allow_origin='*'",
                "--NotebookApp.allow_remote_access=1",
            ],
            env={**os.environ, "JUPYTER_TOKEN": os.environ[JUPYTER_TOKEN_SECRET_NAME]},
        )

        print(f"Jupyter available at => {tunnel.url}")
        jupyter_process.wait()


@stub.local_entrypoint()
def main():
    seed_volume.remote()  
    run_jupyter.remote()
