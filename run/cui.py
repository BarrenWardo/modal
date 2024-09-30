import os
import subprocess
import threading
import time
import modal

DIR = "/root/comfy"
EXTRA_INDEX_URL = "https://pypi.org/simple"
REBUILD = False
HOURS = 12
GPU = "t4"
IDLE = 1200
CONCURRENT_INPUTS = 100
CONCURRENCY_LIMIT = 1
PORT = 8188
CUSTOM_CMD = ""
ARGS = "--listen 0.0.0.0"

app = modal.App(
    "ComfyUI",
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
        "bitsandbytes",
        "cachetools",
        "clip-interrogator",
        "cmake",
        "color_matcher",
        "color-matcher",
        "colour-science",
        "deepdiff",
        "diffusers",
        "einops",
        "facexlib",
        "fairscale",
        "filelock",
        "ftfy",
        "fvcore",
        "git+https://github.com/deforum-studio/deforum.git",
        "git+https://github.com/openai/CLIP.git",
        "git+https://github.com/WASasquatch/cstr",
        "git+https://github.com/WASasquatch/ffmpy.git",
        "git+https://github.com/WASasquatch/img2texture.git",
        "gitpython",
        "GitPython",
        "gradio",
        "gradio_client",
        "huggingface_hub",
        "huggingface-hub",
        "imageio",
        "imageio_ffmpeg",
        "imageio-ffmpeg",
        "imageio[ffmpeg]",
        "importlib_metadata",
        "inference-gpu",
        "insightface",
        "joblib",
        "librosa",
        "matplotlib",
        "matrix-client",
        "mediapipe",
        "moviepy",
        "mss",
        "numba",
        "numexpr",
        "numpy",
        "omegaconf",
        "onnx",
        "onnxruntime",
        "onnxruntime-gpu",
        "open-clip-torch",
        "openai",
        "opencv-contrib-python",
        "opencv-python",
        "opencv-python-headless",
        "opencv-python-headless[ffmpeg]",
        "opensimplex",
        "pandas",
        "peft",
        "piexif",
        "pilgram",
        "Pillow",
        "pillow",
        "pims",
        "pixeloe",
        "protobuf",
        "py-cpuinfo",
        "pydub",
        "PyGithub",
        "pynvml",
        "python-dateutil",
        "pytorch-lightning",
        "PyWavelets",
        "pyyaml",
        "qrcode[pil]",
        "rembg",
        "requests",
        "requirements-parser",
        "rich",
        "rich_argparse",
        "safetensors",
        "scikit-image",
        "scikit-learn",
        "scipy",
        "segment_anything",
        "segment-anything",
        "send2trash",
        "sentencepiece",
        "simpleeval",
        "spaces",
        "spandrel",
        "svglib",
        "timm",
        "torch",
        "torchaudio",
        "torchdiffeq",
        "torchmetrics",
        "torchsde",
        "torchvision",
        "tqdm",
        "transformers",
        "transparent-background",
        "trimesh[easy]",
        "typer",
        "typing-extensions",
        "ultralytics",
        "urllib3",
        "versioneer",
        "xformers",
        "yacs",
        "yapf",
        "yoloworld",
        extra_index_url=EXTRA_INDEX_URL,
        force_build=REBUILD
    )
)

volume = modal.Volume.from_name(
    "CUI", create_if_missing=True
)

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
def run_comfy():
    with modal.forward(PORT) as tunnel:
        cui_folder = os.path.join(DIR, "CUI")
        if os.path.exists(cui_folder):
            cmd = f"cd {cui_folder} && git pull && python main.py {ARGS}"
        else:
            cmd = f"""
            cd {DIR} &&
            git clone https://github.com/comfyanonymous/ComfyUI.git CUI &&
            cd CUI/custom_nodes &&
            git clone https://github.com/ltdrdata/ComfyUI-Manager.git &&
            cd ../.. &&
            python main.py {ARGS}
            """
        
        def delayed_print():
            time.sleep(10)
            print(f"ComfyUI available at => {tunnel.url}")

        threading.Thread(target=delayed_print, daemon=True).start()
        subprocess.run(cmd, shell=True, check=True)

@app.local_entrypoint()
def main():
    run_comfy.remote()