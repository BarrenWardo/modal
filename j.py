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

@stub.function(
        concurrency_limit=1, 
        network_file_systems={CACHE_DIR: nfs}, 
    #    cpu=2,
    #    gpu="t4",
    #    memory=1024,
    #    allow_concurrent_inputs=100,
    #    keep_warm=1,
        timeout=3600
)
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
            env={**os.environ, "JUPYTER_TOKEN": "321"},
        )

        print(f"Jupyter available at => {tunnel.url}")
        jupyter_process.wait()

@stub.local_entrypoint()
def main():
    run_jupyter.remote()
