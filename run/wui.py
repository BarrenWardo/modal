import os
import subprocess
import modal

DIR = "/root/WUI"

app = modal.App(
    "A1111",
    image=modal.Image.debian_slim(python_version="3.11.9")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .pip_install(
        "accelerate",
        "addict",
        "albumentations",
        "av",
        "beautifulsoup4",
        "blendmodes",
        "clean-fid",
        "deepdanbooru",
        "diskcache",
        "dynamicprompts[attentiongrabber,magicprompt]",
        "einops",
        "facexlib",
        "fastapi",
        "fvcore",
        "GitPython",
        "gradio",
        "huggingface_hub",
        "imageio",
        "inflection",
        "insightface",
        "jsonmerge",
        "jsonschema",
        "kornia",
        "lark",
        "lxml",
        "matplotlib",
        "mediapipe",
        "numpy",
        "omegaconf",
        "onnx",
        "open-clip-torch",
        "opencv_contrib_python",
        "opencv_python",
        "opencv_python_headless",
        "opencv-python",
        "packaging",
        "pandas",
        "piexif",
        "Pillow",
        "pillow-avif-plugin",
        "psutil",
        "pycocotools",
        "pydantic",
        "pysocks",
        "python-dotenv",
        "pytorch_lightning",
        "requests",
        "resize-right",
        "rich",
        "safetensors",
        "scikit-image",
        "segment_anything",
        "send2trash",
        "supervision",
        "svglib",
        "tensorflow",
        "timm",
        "tomesd",
        "torch",
        "torchdiffeq",
        "torchsde",
        "tqdm",
        "transformers",
        "ultralytics",
        "uvicorn",
        "xformers",
        "yapf",
        "ZipUnicode",
    )
)

volume = modal.Volume.from_name(
    "WUI", create_if_missing=True
)

@app.function(
    # cpu=2,
    # memory=128,
    gpu="t4",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=1200,
    timeout=12*60*60,  # 3 hours
    # keep_warm=1,
    volumes={DIR: volume},
    _allow_background_volume_commits=True,
)

def run_wui():
    wui_port = 7860
    with modal.forward(wui_port) as tunnel:
        wui_process_cmd = f"cd {DIR} && git pull && python launch.py --allow-code --enable-insecure-extension-access --administrator --log-startup --xformers --update-check --listen --port 7860"
        quickfix = f"git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git WUI"
        wui_process = subprocess.Popen(wui_process_cmd, shell=True)
        print(f"A1111 available at => {tunnel.url}")
        wui_process.wait()

@app.local_entrypoint()
def main():
    run_wui.remote()
