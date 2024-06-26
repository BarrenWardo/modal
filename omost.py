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
    .run_commands(
        "pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"
    )
    .pip_install(
        "diffusers",
        "transformers",
        "gradio",
        "bitsandbytes",
        "accelerate",
        "protobuf",
        "opencv-python",
        "tensorboardX",
        "safetensors",
        "pillow",
        "einops",
        "peft",
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
