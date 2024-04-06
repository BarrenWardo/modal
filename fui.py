import modal
import subprocess

GPU = "t4"
PORT = 7860

fui_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "git",
        "wget",
        "libgl1",
        "libglib2.0-0",
    )
    .run_commands(
        "git clone https://github.com/BarrenWardo/FUI.git",
        "cd FUI",
        "git clone https://github.com/etherealxx/batchlinks-webui.git ./extensions/batchlinks-webui",
        "git clone https://github.com/Bing-su/adetailer.git ./extensions/adetailer",
        "git clone https://github.com/Gourieff/sd-webui-reactor.git ./extensions/sd-webui-reactor",
        "git clone https://github.com/Coyote-A/ultimate-upscale-for-automatic1111.git ./extensions/ultimate-upscale-for-automatic1111",
        "git clone https://github.com/hako-mikan/sd-webui-regional-prompter.git ./extensions/sd-webui-regional-prompter",
        "git clone https://github.com/AlUlkesh/stable-diffusion-webui-images-browser.git ./extensions/stable-diffusion-webui-images-browser",
        "git clone https://github.com/zanllp/sd-webui-infinite-image-browsing.git ./extensions/sd-webui-infinite-image-browsing",
        "git clone https://github.com/thomasasfk/sd-webui-aspect-ratio-helper.git ./extensions/sd-webui-aspect-ratio-helper",
        "git clone https://github.com/catppuccin/stable-diffusion-webui.git ./extensions/stable-diffusion-webui",
        "git clone https://github.com/adieyal/sd-dynamic-prompts.git ./extensions/sd-dynamic-prompts",
        gpu=GPU,
    )
)

stub = modal.Stub("ForgeUI", image=fui_image)

@stub.function(
   #keep_warm=1,
    cpu=2,
    gpu=GPU,
)

@modal.web_server(PORT,startup_timeout=180)

def run():
    START_COMMAND = [
    "python",
    "launch.py",
    "--listen",
    "--enable-insecure-extension-access",
    #"--share",
    "--skip-torch-cuda-test",
    "--xformers",
    "--port",
    f'"{PORT}"',
    ]
    subprocess.Popen(START_COMMAND, shell=True)