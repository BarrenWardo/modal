import modal

stub = modal.Stub()

# Start with a base Debian slim image with Python 3.10
image = modal.Image.debian_slim(python_version="3.10")

# Install system packages using apt
image = image.apt_install("git", "wget", "aria2c", "unzip")

# Define a Modal function using the customized image
@stub.function(image=image)
@modal.web_server(port=7860)
def web_server():
    # Run the commands to set up and launch the web server
    modal.subprocess.run(["git", "clone", "https://github.com/BarrenWardo/FUI"], check=True)
    # Navigate to the cloned directory and install requirements
    os.chdir("FUI")
    modal.subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    # Launch the Python script which starts a web server listening on port 7860
    modal.subprocess.run(["python", "launch.py", "--xformers", "--enable-insecure-extension-access", "--update-all-extensions"], check=True)

@stub.local_entrypoint()
def main():
    with stub.run():
        web_server()

if __name__ == "__main__":
    main()
    
