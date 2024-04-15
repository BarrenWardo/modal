import os
import subprocess
import modal

def extract_jupyter_secrets():
    token = os.environ.get("Token")
    gpu = os.environ.get("GPU")
    timeout = int(os.environ.get("Timeout", 3600))
    return token, gpu, timeout

stub = modal.Stub(
    image=modal.Image.debian_slim().pip_install(
        "jupyter",
    )
)
nfs = modal.NetworkFileSystem.from_name(
    "sd", create_if_missing=True
)

CACHE_DIR = "/root/SD"

@stub.function(secrets=[modal.Secret.from_name("jupyter secrets")])
def get_secrets():
    token = os.environ.get("Token")
    gpu = os.environ.get("GPU")
    timeout = int(os.environ.get("Timeout", 3600))
    return token, gpu, timeout

@stub.function(network_file_systems={CACHE_DIR: nfs})
def seed_volume():
    pass

@stub.function(concurrency_limit=1, network_file_systems={CACHE_DIR: nfs})
def run_jupyter(token, gpu, timeout):
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
            env={**os.environ, "JUPYTER_TOKEN": token},
        )

        print(f"Jupyter available at => {tunnel.url}")
        jupyter_process.wait()

@stub.local_entrypoint()
def main():
    token, gpu, timeout = get_secrets()
    seed_volume.remote()  
    run_jupyter.remote(token, gpu, timeout)
