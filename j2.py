import os
import subprocess
import modal

stub = modal.Stub()
volume = modal.Volume.from_name("sd-volume", create_if_missing=True)

@stub.function(volumes={"/root/SD": volume})
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

        # Reload volume to fetch latest changes
        volume.reload()

        # Commit any changes made during Jupyter session
        volume.commit()

@stub.local_entrypoint()
def main():
    run_jupyter.remote()
