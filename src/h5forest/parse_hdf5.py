import sys
import json
import h5py


def get_item_info(item):
    """Extract information from a group or dataset to a dictionary."""
    if isinstance(item, h5py.Dataset):
        return {
            "type": "dataset",
            "name": item.name.split("/")[-1],
            "path": item.name,
            "datatype": str(item.dtype),
            "shape": item.shape,
            "has_children": False,  # Datasets don't have children in the HDF5 structure sense
        }
    elif isinstance(item, h5py.Group):
        return {
            "type": "group",
            "name": item.name.split("/")[-1],
            "path": item.name,
            "has_children": bool(
                item.keys()
            ),  # True if the group contains any subgroups or datasets
        }


def parse_hdf5_level(file_path, group_path="/"):
    """Parse the HDF5 file at the specified level and output JSON."""
    structure = []
    with h5py.File(file_path, "r") as file:
        group = file[group_path]
        for key in group.keys():
            item = group[key]
            structure.append(get_item_info(item))
    return structure


def main():
    """Parse the HDF5 file and print the structure as JSON."""
    if len(sys.argv) < 2:
        print("Usage: python parse_hdf5.py <file_path> [group_path]")
        sys.exit(1)

    file_path = sys.argv[1]
    group_path = sys.argv[2] if len(sys.argv) > 2 else "/"

    structure = parse_hdf5_level(file_path, group_path)
    print(json.dumps(structure, indent=4))


if __name__ == "__main__":
    main()
