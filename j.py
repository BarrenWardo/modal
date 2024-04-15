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

@stub.function(network_file_systems={CACHE_DIR: nfs})
def seed_volume():
    pass

@stub.function(concurrency_limit=1, network_file_systems={CACHE_DIR: nfs}, timeout=int(os.environ.get("Timeout", 3600)), secrets=[modal.Secret.from_name("jupyter secrets"), modal.Secret.from_name("GPU")])
def run_jupyter():
    jupyter_port = 8888
    gpu_secret = os.environ.get("GPU", None)

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
            env={**os.environ, "JUPYTER_TOKEN": os.environ.get("Token")},
        )

        print(f"Jupyter available at => {tunnel.url}")
        jupyter_process.wait()

@stub.local_entrypoint()
def main():
    seed_volume.remote()  
    run_jupyter.remote()
