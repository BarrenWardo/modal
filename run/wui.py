import os
import subprocess
import threading
import time
import modal

DIR = "/root/WUI"
EXTRA_INDEX_URL = "https://pypi.org/simple"
REBUILD = False
HOURS = 12
GPU = "t4"
IDLE = 1200
CONCURRENT_INPUTS = 100
CONCURRENCY_LIMIT = 1
PORT = 7860
CUSTOM_CMD = ""
ARGS = f"--allow-code --enable-insecure-extension-access --administrator --log-startup --xformers --update-check --listen --api --port {PORT}"

app = modal.App(
    "A1111",
    image=modal.Image.debian_slim(python_version="3.11.9")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "aria2",
        force_build=REBUILD,
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
        extra_index_url=EXTRA_INDEX_URL,
        force_build=REBUILD
    )
)

volume = modal.Volume.from_name("WUI", create_if_missing=True)

@app.function(
    concurrency_limit=CONCURRENCY_LIMIT,
    allow_concurrent_inputs=CONCURRENT_INPUTS,
    container_idle_timeout=IDLE,
    timeout=HOURS * 60 * 60,
    volumes={DIR: volume},
    #cpu=2,
    #memory=128,
    #keep_warm=1,
    gpu=GPU,
)

def run_wui():
    with modal.forward(PORT) as tunnel:
        wui_folder = os.path.join(DIR, "WUI")
        if os.path.exists(wui_folder):
            cmd = f"cd {wui_folder} && git pull && python launch.py {ARGS}"
        else:
            cmd = f"""
            cd {DIR} &&
            git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git WUI &&
            python launch.py {ARGS}
            """
        
        def delayed_print():
            time.sleep(10)
            print(f"A1111 available at => {tunnel.url}")

        threading.Thread(target=delayed_print, daemon=True).start()
        subprocess.run(cmd, shell=True, check=True)

@app.local_entrypoint()
def main():
    run_wui.remote()