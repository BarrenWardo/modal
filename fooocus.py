import os
import subprocess
import modal

stub = modal.Stub(
    image=modal.Image.debian_slim()
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
    )
    .run_commands(
        "git clone https://github.com/BarrenWardo/Fooocus",
        "cd /Fooocus",
    )
)

@stub.function(
        cpu=4,
        gpu="t4",
        memory=256,
        keep_warm=1,
        timeout=3600,
        concurrency_limit=1,
)
def run_fooocus():
    fooocus_port = 7860
    with modal.forward(fooocus_port) as tunnel:
        fooocus_process = subprocess.Popen(
            [
                "python",
                "entry_with_update.py",
                f"--port={fooocus_port}",
            ],
            cwd="Fooocus"
        )

        print(f"Fooocus available at => {tunnel.url}")
        fooocus_process.wait()

@stub.local_entrypoint()
def main():
    run_fooocus.remote()
