import os
import subprocess
import modal

app = modal.App(
    "JupyterLab",
    image=modal.Image.debian_slim()
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .pip_install(
        "jupyterlab",
    )
)
volume = modal.Volume.from_name("jupyterlab", create_if_missing=True)

@app.function(
    volumes={"/root/jupyterlab": volume},
    #cpu=2,
    #memory=128,
    #gpu="any",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=120,
    timeout=1800,
    #keep_warm=1,
    #enable_memory_snapshot=True,
    _allow_background_volume_commits=True,
)

jupyterlab_port = 8888
def run_jupyterlab():
    jupyterlab_process = subprocess.Popen(
        [
            "jupyter",
            "lab",
            "--no-browser",
            "--allow-root",
            "--ip=0.0.0.0",
            f"--port={jupyterlab_port}",
            "--ServerApp.allow_origin='*'",
            "--ServerApp.allow_remote_access=1",
        ],
        env={**os.environ, "JUPYTERLAB_TOKEN": "321"},
    )
    jupyterlab_process.wait()
        
@app.local_entrypoint()
def main():
    run_jupyterlab.remote()
