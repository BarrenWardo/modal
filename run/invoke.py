import os
import subprocess
import modal

DIR = "/root/invoke"
INVOKEAI_DIR = f"{DIR}/invokeai"
CONFIG_FILE = f"{INVOKEAI_DIR}/invokeai.yaml"
EXTRA_INDEX_URL = "https://pypi.org/simple"
REBUILD = False
BETA = True
HOURS = 12
YAML = "https://gist.githubusercontent.com/BarrenWardo/128c628052d8bc4bea589645bdd4732a/raw/invokeai.yaml"
GPU = "t4"
IDLE = 1200
CONCURRENT_INPUTS = 100
CONCURRENCY_LIMIT = 1

# Initialize the Modal app
app = modal.App(
    "InvokeAI",
    image=modal.Image.debian_slim(python_version="3.10.14")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "libgl1-mesa-glx",
        "build-essential",
        "python3-opencv",
        "libopencv-dev",
        force_build=REBUILD,
    )
    .pip_install(
        "torch",
        "torchvision",
        "torchaudio",
        "pypatchmatch",
        extra_index_url=EXTRA_INDEX_URL,
        force_build=REBUILD,
    )
    .pip_install(
        "InvokeAI[xformers]",
        extra_index_url=EXTRA_INDEX_URL,
        force_build=REBUILD,
        pre=BETA,
    )
)

volume = modal.Volume.from_name("Invoke", create_if_missing=True)

def check_patchmatch_installation():
    """Check if pypatchmatch and patch_match are correctly installed."""
    try:
        import patchmatch
        from patchmatch import patch_match
        print("pypatchmatch and patch_match are successfully imported.")
        return True
    except ImportError as e:
        print(f"ImportError: {e}")
        return False

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
def run_invokeai():
    invokeai_port = 9090
    with modal.forward(invokeai_port) as tunnel:
        os.makedirs(INVOKEAI_DIR, exist_ok=True)
        
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            print(f"Deleted existing configuration file: {CONFIG_FILE}")
        
        subprocess.run(
            ["wget", YAML, "-O", CONFIG_FILE],
            check=True,
            capture_output=True,
            text=True,
        )

        if not check_patchmatch_installation():
            print("pypatchmatch is not installed or not functional. Exiting.")
            return

        invokeai_process = subprocess.Popen(
            ["invokeai-web", "--root", INVOKEAI_DIR],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"InvokeAI available at => {tunnel.url}")
        invokeai_process.wait()

@app.local_entrypoint()
def main():
    run_invokeai.remote()