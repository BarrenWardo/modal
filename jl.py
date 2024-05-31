import os
import subprocess
import modal
import re

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
    # cpu=2,
    # memory=4096,
    # gpu="any",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=120,
    timeout=1800,
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

        while True:
            output = jupyterlab_process.stdout.readline()
            if output:
                print(output.strip())
                # Parse the URL from the logs
                if "http://127.0.0.1:8888/lab" in output:
                    url = re.search(r'http://127.0.0.1:8888/lab\?token=\w+', output)
                    if url:
                        url = url.group(0)
                        print(f"JupyterLab available at => {tunnel.url}")
                        print(f"Access JupyterLab at {url.replace('http://127.0.0.1:8888', tunnel.url)}")
                    else:
                        # If there's no token in the URL
                        print(f"JupyterLab available at => {tunnel.url}")
                        print(f"Access JupyterLab at {tunnel.url}/lab")
                    break
            elif jupyterlab_process.poll() is not None:
                break

        jupyterlab_process.wait()

@app.local_entrypoint()
def main():
    run_jupyterlab.remote()
