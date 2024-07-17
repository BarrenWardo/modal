import os
import subprocess
import modal

DIR = "/root/Fooocus"

app = modal.App(
    "Fooocus",
    image=modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .pip_install(
        "pip",
        "packaging",
        "torchsde==0.2.5",
        "einops==0.4.1",
        "transformers==4.30.2",
        "safetensors==0.3.1",
        "accelerate==0.21.0",
        "pyyaml==6.0",
        "Pillow==9.2.0",
        "scipy==1.9.3",
        "tqdm==4.64.1",
        "psutil==5.9.5",
        "pytorch_lightning==1.9.4",
        "omegaconf==2.2.3",
        "gradio==3.41.2",
        "pygit2==1.12.2",
        "opencv-contrib-python==4.8.0.74",
        "httpx==0.24.1",
        "onnxruntime==1.16.3",
        "timm==0.9.2",
        "xformers",
    )
)

volume = modal.Volume.from_name(
    "Fooocus", create_if_missing=True
)

@app.function(
    # cpu=2,
    # memory=128,
    gpu="t4",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=1200,
    timeout=10800,  # 3 hours
    # keep_warm=1,
    volumes={DIR: volume},
    _allow_background_volume_commits=True,
)

def run_app():
    app_port = 7865
    with modal.forward(app_port) as tunnel:
        app_cmd = f"cd {DIR} && git pull && python entry_with_update.py --listen 0.0.0.0 --port 7865 --multi-user --preview-option auto"
        cmd = f"git clone https://github.com/lllyasviel/Fooocus.git"
        app_start = subprocess.Popen(app_cmd, shell=True)
        print(f"Fooocus available at => {tunnel.url}")
        app_start.wait()

@app.local_entrypoint()
def main():
    run_app.remote()
