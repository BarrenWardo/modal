import os
import subprocess
import modal

app = modal.App(
    "Jupyter",
    image=modal.Image.debian_slim()
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .pip_install(
        "jupyter",
    )
)
volume = modal.Volume.from_name("jupyter", create_if_missing=True)

@app.function(
    volumes={"/root/jupyter": volume},
    #cpu=2,
    #memory=128,
    #gpu="any",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    #container_idle_timeout=60,
    timeout=1800,
    #keep_warm=1,
    #enable_memory_snapshot=True,
    _allow_background_volume_commits=True,
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
        
@app.local_entrypoint()
def main():
    run_jupyter.remote()
