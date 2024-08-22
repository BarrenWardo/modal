import os
import subprocess
import modal

DIR = "/root/comfy"

app = modal.App(
    "ComfyUI",
    image=modal.Image.debian_slim(python_version="3.11.9")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "aria2",
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
    )
)

volume = modal.Volume.from_name(
    "CUI", create_if_missing=True
)

@app.function(
    # cpu=2,
    # memory=128,
    gpu="t4",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=1200,
    timeout=3*60*60,  # 3 hours
    # keep_warm=1,
    volumes={DIR: volume},
)

def run_comfy():
    comfy_port = 8188
    with modal.forward(comfy_port) as tunnel:
        cui_folder = os.path.join(DIR, "CUI")
        if os.path.exists(cui_folder):
            comfy_process_cmd = f"cd {cui_folder} && git pull && python main.py --listen 0.0.0.0"
        else:
            comfy_process_cmd = f"cd {DIR} && git clone https://github.com/comfyanonymous/ComfyUI.git CUI && cd CUI/custom_nodes && git clone https://github.com/ltdrdata/ComfyUI-Manager.git && cd ../.. && python main.py"
        quickfix = f"cd {cui_folder}/models/unet && wget https://huggingface.co/BarrenWardo/SD-Models/resolve/main/flux1-dev.sft"
        comfy_process = subprocess.Popen(comfy_process_cmd, shell=True)
        print(f"ComfyUI available at => {tunnel.url}")
        comfy_process.wait()

@app.local_entrypoint()
def main():
    run_comfy.remote()
