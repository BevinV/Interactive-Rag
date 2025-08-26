import os

def init_storage():
    os.makedirs("storage/docs", exist_ok=True)
    print("Storage directories created")

if __name__ == "__main__":
    init_storage()