import os
import subprocess
import modal

DIR = "/root/invoke"
INVOKEAI_DIR = f"{DIR}/invokeai"
CONFIG_FILE = f"{INVOKEAI_DIR}/invokeai.yaml"
REBUILD = False

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
        "pip",
        "InvokeAI[xformers]",
        "torch",
        "torchvision",
        "torchaudio",
        "pypatchmatch",
        extra_index_url="https://pypi.org/simple",
        force_build=REBUILD,
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
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=1200,
    timeout=3 * 60 * 60,  # 3 hours
    volumes={DIR: volume},
    #cpu-2,
    #memory=128,
    #keep_warm=1,
    gpu="t4",
)
def run_invokeai():
    invokeai_port = 9090
    with modal.forward(invokeai_port) as tunnel:
        # Ensure the directory exists
        os.makedirs(INVOKEAI_DIR, exist_ok=True)

        # Delete existing configuration file if it exists
        if os.path.exists(CONFIG_FILE):
            try:
                os.remove(CONFIG_FILE)
                print(f"Deleted existing configuration file: {CONFIG_FILE}")
            except OSError as e:
                print(f"Error deleting file {CONFIG_FILE}: {e}")
                return

        # Download the latest configuration file
        download_url = "https://gist.githubusercontent.com/BarrenWardo/128c628052d8bc4bea589645bdd4732a/raw/invokeai.yaml"
        wget_process = subprocess.run(
            ["wget", download_url, "-O", CONFIG_FILE],
            capture_output=True,
            text=True,
        )

        if wget_process.returncode != 0:
            print(f"Error downloading configuration file: {wget_process.stderr}")
            return

        # Check if pypatchmatch is installed and functional
        if not check_patchmatch_installation():
            print("pypatchmatch is not installed or not functional. Exiting.")
            return

        # Start InvokeAI server
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
