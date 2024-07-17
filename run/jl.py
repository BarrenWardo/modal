import os
import subprocess
import modal

# Initialize the Modal app
app = modal.App(
    "JupyterLab",
    image=modal.Image.debian_slim()
    .micromamba()
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "htop",
    )
    .pip_install(
        "jupyterlab",
        "nvitop",
    )
)

# Define a persistent volume
volume = modal.Volume.from_name("jupyterlab", create_if_missing=True)

# Define the function to run JupyterLab
@app.function(
    volumes={"/root/jl": volume},
    # cpu=2,
    # memory=128,
    gpu="t4",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=1200,
    timeout=10800,  # 3 hours
    # keep_warm=1,
    _allow_background_volume_commits=True,
)
def run_jupyterlab():
    jupyterlab_port = 8888
    with modal.forward(jupyterlab_port) as tunnel:
        jupyterlab_process = subprocess.Popen(
            [
                "jupyter",
                "lab",
                "--no-browser",
                "--allow-root",
                "--ip=0.0.0.0",
                f"--port={jupyterlab_port}",
                "--ServerApp.token=''",
                "--ServerApp.password=''",
                "--ServerApp.allow_origin='*'",
                "--ServerApp.allow_remote_access=1",
            ],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"JupyterLab available at => {tunnel.url}")
        jupyterlab_process.wait()

# Define the local entry point
@app.local_entrypoint()
def main():
    run_jupyterlab.remote()
