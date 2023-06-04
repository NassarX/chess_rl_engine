import platform
import os

import requests
import zipfile
import shutil
# from logger import Logger
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def download_stockfish_binary(path) -> str:
    os_name = platform.system()

    if os_name == "Windows":
        download_url = "https://stockfishchess.org/files/stockfish_15_win_x64_ssse.zip"
        binary_path = "stockfish_15_win_x64_ssse/stockfish_15_x64_ssse.exe"
        binary_name = "stockfish.exe"
    elif os_name == "Linux":
        download_url = "https://stockfishchess.org/files/stockfish_15_linux_x64_ssse.zip"
        binary_path = "stockfish_15_linux_x64_ssse/stockfish_15_x64_ssse"
        binary_name = "stockfish"
    elif os_name == "Darwin":
        download_url = "https://stockfishchess.org/files/stockfish-11-mac.zip"
        binary_path = "stockfish-11-mac/Mac/stockfish-11-64"
        binary_name = "stockfish"
    else:
        print("Unsupported operating system:", os_name)
        return

    # Download the zip file
    response = requests.get(download_url)
    if response.status_code == 200:
        # Save the zip file
        with open("stockfish.zip", "wb") as file:
            file.write(response.content)

        # Extract the contents of the zip file
        with zipfile.ZipFile("stockfish.zip", "r") as zip_ref:
            zip_ref.extractall()

        # Move the binary file to the bin directory
        dest_dir = os.path.join(os.getcwd(), path)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, binary_name)
        shutil.move(binary_path, dest_path)

        # Update file permissions
        os.chmod(dest_path, 0o755)

        # Clean up
        os.remove("stockfish.zip")

        if os_name == "Darwin":
            shutil.rmtree(os.path.dirname(os.path.dirname(binary_path)))
            shutil.rmtree("__MACOSX")
        else:
            shutil.rmtree(os.path.dirname(binary_path))

        print("Stockfish downloaded and configured successfully.")
        return dest_path
    else:
        print("Failed to download Stockfish.")


def generate_stockfish_data(callback_game, dataset, stockfish_bin, dest_path, depth=1,
                            random_depth=False, num_games=100, workers=2):
    # logger = Logger.get_instance()
    print("Generating data with Stockfish...")
    pbar = tqdm(total=num_games)

    # Execute the game function in parallel using the ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as executor:
        for _ in range(num_games):
            executor.submit(callback_game(stockfish_bin=stockfish_bin, dataset=dataset, depth=depth,
                                          random_dep=random_depth, tqbar=pbar))

    pbar.close()

    # logger.info("Saving dataset...")

    print("Saving dataset...")
    dataset.save(dest_path)
    print(f"Dataset saved to {dest_path}")
