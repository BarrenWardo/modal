import os
import subprocess
import modal

modal_gpu = "t4"
fui_dir = "/root/FUI"
server_timeout = 1800

app = modal.App(
    "Forge",
    image=modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .pip_install(
        "GitPython",
        "Pillow",
        "accelerate",
        "blendmodes",
        "clean-fid",
        "einops",
        "facexlib",
        "fastapi>=0.90.1",
        "gradio==3.41.2",
        "inflection",
        "jsonmerge",
        "kornia",
        "lark",
        "numpy",
        "omegaconf",
        "open-clip-torch",
        "piexif",
        "psutil",
        "pytorch_lightning",
        "requests",
        "resize-right",
        "safetensors",
        "scikit-image>=0.19",
        "tomesd",
        "torch",
        "torchdiffeq",
        "torchsde",
        "transformers==4.30.2",
        "insightface",
    )
)

volume = modal.Volume.from_name(
    "FUI", create_if_missing=True
)

@app.function(
    cpu=2,
    gpu=modal_gpu,
    memory=128,
    keep_warm=1,
    concurrency_limit=1,
    volumes={fui_dir: volume},
    _allow_background_volume_commits=True,
    allow_concurrent_inputs=100,
)

@modal.web_server(port=7860, startup_timeout=server_timeout)

def run_fui():
    fui_folder = os.path.join(fui_dir, "FUI")
    if os.path.exists(fui_folder):
        fui_start = f"""
            cd {fui_folder} && git pull && pip install -r requirements.txt && python launch.py --listen --enable-insecure-extension-access
        """
    else:
        fui_start = f"""
            cd {fui_dir} && git clone https://github.com/BarrenWardo/FUI.git && cd FUI && pip install -r requirements.txt && python launch.py --listen --enable-insecure-extension-access
        """
    subprocess.Popen(fui_start, shell=True)
