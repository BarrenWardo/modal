import os
import subprocess
import modal

omost_port = 7860
server_timeout = 1200
modal_gpu = "t4"
DIR = "/root/omost"

app = modal.App(
    "Omost",
    image=modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .pip_install(
        "diffusers==0.28.0",
        "transformers==4.41.1",
        "gradio==4.31.5",
        "bitsandbytes==0.43.1",
        "accelerate==0.30.1",
        "protobuf==3.20",
        "opencv-python",
        "tensorboardX",
        "safetensors",
        "pillow",
        "einops",
        "torch",
        "peft",
        "torchvision",
        index_url="https://download.pytorch.org/whl/cu121",
    )
)

volume = modal.Volume.from_name(
    "omost", create_if_missing=True
)

@app.function(
        cpu=2,
        gpu=modal_gpu,
        memory=128,
        #keep_warm=1,
        concurrency_limit=1,
        volumes={DIR: volume},
        _allow_background_volume_commits=True,
        allow_concurrent_inputs=100,
        timeout=server_timeout,
        container_idle_timeout=180,
)

@modal.web_server(port=omost_port, startup_timeout=server_timeout)

def run_omost():
    omost_folder = os.path.join(DIR, "Omost")
    if os.path.exists(omost_folder):
        omost_process = f"""
            cd {omost_folder} && python gradio_app.py
        """
    else:
        omost_process = f"""
            cd {DIR} && git clone https://github.com/BarrenWardo/Omost.git && cd Omost && python gradio_app.py
            
        """
    subprocess.Popen(omost_process, shell=True)
