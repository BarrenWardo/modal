import os
import subprocess
import modal

# Initialize the Modal app
app = modal.App(
    "InvokeAI",
    image=modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "libgl1-mesa-glx",
        "build-essential",
        "python3-opencv",
        "libopencv-dev",
    )
    .pip_install(
        "InvokeAI[xformers]",
        "torch",
        "torchvision",
        "torchaudio",
        "pypatchmatch",
    )
)

# Define the function to run InvokeAI
@app.function(
    # cpu=2,
    # memory=128,
    gpu="t4",
    concurrency_limit=1,
    allow_concurrent_inputs=100,
    container_idle_timeout=1200,
    timeout=10800,  # 3 hours
    # keep_warm=1,
)
def run_invokeai():
    invokeai_port = 9090
    with modal.forward(invokeai_port) as tunnel:
        # Create the directory
        mkdir_process = subprocess.Popen(
            ["mkdir", "-p", "invokeai"],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        mkdir_stdout, mkdir_stderr = mkdir_process.communicate()
        if mkdir_process.returncode != 0:
            print(f"Error creating directory: {mkdir_stderr}")
            return

        # Download the configuration file using wget
        wget_process = subprocess.Popen(
            [
                "wget",
                "https://gist.githubusercontent.com/BarrenWardo/128c628052d8bc4bea589645bdd4732a/raw/invokeai.yaml",
                "-O",
                "invokeai/invokeai.yaml",
            ],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        wget_stdout, wget_stderr = wget_process.communicate()
        if wget_process.returncode != 0:
            print(f"Error downloading configuration file: {wget_stderr}")
            return

        # Start the InvokeAI web server
        invokeai_process = subprocess.Popen(
            ["invokeai-web"],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"InvokeAI available at => {tunnel.url}")
        invokeai_process.wait()

# Define the local entry point
@app.local_entrypoint()
def main():
    run_invokeai.remote()
