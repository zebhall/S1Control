import os
import csv


def rename_files(csv_filename):
    with open(csv_filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            info_fields = row["Info Fields (Combined)"].split(",")
            new_filename = info_fields[0].strip()
            if row["Sanity Check"] == "FAIL":
                new_filename = "FAIL_" + new_filename
            pdz_number = int(row["PDZ"])
            pdz_filename = f"{pdz_number:05d}-Spectrum Only.pdz"
            if os.path.exists(pdz_filename):
                os.rename(pdz_filename, new_filename + ".pdz")
                print(f"Renamed {pdz_filename} to {new_filename}.pdz")
            else:
                print(
                    f"PDZ file {pdz_filename} not found. Checking for GeoExploration version."
                )
                pdz_filename = f"{pdz_number:05d}-GeoExploration.pdz"
                if os.path.exists(pdz_filename):
                    os.rename(pdz_filename, new_filename + ".pdz")
                    print(f"Renamed {pdz_filename} to {new_filename}.pdz")
                else:
                    print(f"PDZ file {pdz_filename} not found. Moving on to next file.")


if __name__ == "__main__":
    csv_files = [
        filename
        for filename in os.listdir()
        if filename.startswith("Results_") and filename.endswith(".csv")
    ]
    if len(csv_files) == 0:
        print("No CSV file starting with 'Results_' found in the current directory.")
    elif len(csv_files) > 1:
        print(
            "Multiple CSV files starting with 'Results_' found in the current directory. Please ensure only one such file exists."
        )
    else:
        rename_files(csv_files[0])
    input()
