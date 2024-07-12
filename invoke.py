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
        invokeai_process = subprocess.Popen(
            [
                "invokeai-web",
            ],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(f"InvokeAi available at => {tunnel.url}")
        invokeai_process.wait()

# Define the local entry point
@app.local_entrypoint()
def main():
    run_invokeai.remote()
