import os
import subprocess
import time
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

@stub.function(secrets=[modal.Secret.from_name("jupyter secrets")])
def get_secrets():
    token = os.environ.get("Token")
    gpu = os.environ.get("GPU")
    timeout = int(os.environ.get("Timeout"))
    return token, gpu, timeout

@stub.function(concurrency_limit=1, network_file_systems={CACHE_DIR: nfs}, timeout=timeout)
def run_jupyter(token: str, gpu: str, timeout: int):
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

        try:
            end_time = time.time() + timeout
            while time.time() < end_time:
                time.sleep(5)
            print(f"Reached end of {timeout} second timeout period. Exiting...")
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            jupyter_process.kill()

@stub.local_entrypoint()
def main():
    token, gpu, timeout = get_secrets()
    if gpu is not None:
        run_jupyter.set_gpu(modal.gpu.from_name(gpu))
    run_jupyter.remote(token, gpu, timeout)
