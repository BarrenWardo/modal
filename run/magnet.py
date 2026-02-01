import os
import subprocess
import modal

URL = "MAGNET_URL" 
DEST_DIR = "/root/dl"

image = (
    modal.Image.debian_slim()
    .apt_install("aria2")
)

app = modal.App("Magnet-Downloader", image=image)
volume = modal.Volume.from_name("dl", create_if_missing=True)

@app.function(
    volumes={DEST_DIR: volume},
    max_containers=1,      
    scaledown_window=60*1, 
    timeout=3600*1,        
)
def run_dl(url: str):
    if not url:
        return

    print(f"Status: Initializing download for {url}")

    cmd = [
        "aria2c",
        "-d", DEST_DIR,
        "--seed-time=0",               # Stop seeding immediately
        "--bt-stop-timeout=600",       # Kill if no peers found
        
        "--max-connection-per-server=16", 
        "--split=16",                  # Split files into more pieces
        "--min-split-size=1M",         # Allow splitting even for small files
        "--file-allocation=falloc",    # Instantly reserves disk space (fastest on Linux)
        "--bt-max-peers=55",           # Increase peer count for faster swarm speeds
        "--enable-dht=true",           # Distributed Hash Table for more peer discovery
        "--bt-enable-lpd=true",        # Local Peer Discovery
        "--bt-request-peer-speed-limit=0", # No limit on requesting peers
        "--optimize-concurrent-downloads=true",
        "--disk-cache=64M",            # Cache in RAM to reduce Volume write overhead
        
        "--summary-interval=15",
        url
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()
    
    if process.returncode == 0:
        print("\nSuccess: Torrent download finished.")
        total_size = subprocess.check_output(["du", "-sh", DEST_DIR]).split()[0].decode('utf-8')
        print(f"Total size in Volume: {total_size}")
        volume.commit()
    else:
        print(f"\nError: aria2 exited with code {process.returncode}")

@app.local_entrypoint()
def main():
    run_dl.remote(URL)
