from pathlib import Path


PATH = Path(__file__).parent / "data" / "f1-elo" / "v1.0.0"


def download_dataset():
    import kagglehub
    path = kagglehub.dataset_download(
        handle="rohanrao/formula-1-world-championship-1950-2020",
        output_dir=PATH,
    )
    print("Path to dataset files:", path)


if __name__ == "__main__":
    download_dataset()
