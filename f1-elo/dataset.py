import sys
from pathlib import Path

ROHANRAO = "rohanrao"
ATHARVRANJAN = "atharvranjan"

_dataset_handles = {
    ROHANRAO: "rohanrao/formula-1-world-championship-1950-2020",
    ATHARVRANJAN: "atharvranjan/formula-1-world-championship-1950-present",
}


def path(dataset):
    return Path(__file__).parent / "data" / "f1-elo" / dataset


def download_dataset(dataset=ROHANRAO):
    import kagglehub
    handle = _dataset_handles[dataset]
    output_path = kagglehub.dataset_download(
        handle=handle,
        output_dir=path(dataset),
    )
    print("Path to dataset files:", output_path)


if __name__ == "__main__":
    download_dataset(sys.argv[1])
