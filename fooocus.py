import os
import subprocess
import modal

stub = modal.Stub(
    image=modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .run_commands(
        "git clone https://github.com/BarrenWardo/Fooocus /Fooocus",
    )
    .pip_install(
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
        "onnxruntime",
        "timm==0.9.2",
        gpu="t4",
    )  
)
@stub.function(
        cpu=4,
        gpu="t4",
        memory=256,
        keep_warm=1,
        timeout=3600,
        concurrency_limit=1,
)
def run_fooocus():
    fooocus_port = 7860
        fooocus_process = f"""
        cd /Fooocus && python entry_with_update.py --listen --port {fooocus_port} --share
        """
        subprocess.Popen(fooocus_process, shell=True)
