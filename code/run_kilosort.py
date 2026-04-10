import sys
from argparse import ArgumentParser
from typing import Optional, Sequence
import logging
from pathlib import Path
import json

import torch

from probeinterface import read_spikeglx, write_prb, ProbeGroup
from kilosort import __version__ as kilosort_version
from kilosort import DEFAULT_SETTINGS, run_kilosort
from kilosort.io import load_probe


def set_up_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info(f"Kilosort version {kilosort_version}")


def find(
    glob: str,
    filter: str = "",
    parent: Path = None,
) -> list:
    """Search for a list of matches to the given glob pattern, optionally filtering results that contain the given filter."""
    if glob.startswith("/"):
        # Search from an absolute path.
        matches = Path("/").glob(glob[1:])
    else:
        # Search from the given or current working directory.
        if parent is None:
            parent = Path()
        matches = parent.glob(glob)
    matching_paths = [match for match in matches if filter in match.as_posix()]
    logging.info(f"Found {len(matching_paths)} matches with filter '{filter}' for pattern: {glob}")
    return matching_paths


def find_one(
    glob: str,
    filter: str = "",
    default: Path = None,
    none_ok: bool = False,
    parent: Path = None,
) -> Path:
    """Search for a single match to the given glob pattern, optionally filtering duplicate glob matches using the given filter."""
    matching_paths = find(glob, filter, parent)
    if len(matching_paths) == 1:
        first_match = matching_paths[0]
        logging.info(f"Found one match: {first_match}")
        return first_match
    elif len(matching_paths) > 1:
        logging.error(f"Found multiple matches, please remove all but one: {matching_paths}")
        raise ValueError(f"Too many matches found.")
    elif default is not None or none_ok:
        return default
    else:
        raise ValueError(f"No match found.")


def parse_meta(
    meta_file: Path
):
    """Parse a SpikeGLX .meta file into a Python dict."""
    meta_info = {}
    with open(meta_file, 'r') as f:
        for line in f:
            line_parts = line.split("=", maxsplit=1)
            key = line_parts[0].strip()
            if len(line_parts) > 1:
                raw_value = line_parts[1].strip()
                try:
                    value = int(raw_value)
                except:
                    try:
                        value = float(raw_value)
                    except:
                        value = raw_value
            else:
                value = None
            meta_info[key] = value
    return meta_info


def find_probes_and_sort(
    probe_ids: list[str],
    ap_meta_pattern: str,
    kilosort_settings_pattern: str,
    results_path: Path
):
    # Sort out CPU vs GPU mode.
    if torch.cuda.is_available():
        logging.info("PyTorch thinks GPU/CUDA is available.")
        device = torch.device('cuda')
    else:
        logging.warning("PyTorch thinks only CPU is available.")
        device = torch.device('cpu')

    logging.info(f"Using PyTorch device: {device}")

    # If we never find a recording to sort, raise an error at the end.
    probe_count = 0

    for probe_id in probe_ids:
        logging.info(f"Looking for probe {probe_id}")
        ap_meta_path = find_one(ap_meta_pattern, probe_id, none_ok=True)
        if ap_meta_path is None:
            logging.info(f"No match for {probe_id}")
            continue
        logging.info(f"Found probe metadata: {ap_meta_path}")

        metadata = parse_meta(ap_meta_path)
        binary_channel_count = metadata['nSavedChans']
        logging.info(f"Expecting binary recording with {binary_channel_count} saved channels.")

        ab_bin_path = ap_meta_path.with_suffix(".bin")
        if not ab_bin_path.exists():
            logging.info(f"No binary recording found at {ab_bin_path}")
            continue
        logging.info(f"Found binary recording: {ab_bin_path}")

        # Count up matched probes for summary and/or error at the end.
        probe_count += 1

        # Save results for each probe in a separate subdir.
        probe_results_path = Path(results_path, probe_id)
        probe_results_path.mkdir(exist_ok=True, parents=True)

        # Convert SpikeGlx .meta probe description to Kilosort 4 .prb format.
        prb_path = Path(probe_results_path, ap_meta_path.with_suffix(".prb").name)
        logging.info(f"Converting '{ap_meta_path}' to '{prb_path}'")
        probe_info = read_spikeglx(ap_meta_path)
        probe_group = ProbeGroup()
        probe_group.add_probe(probe_info)
        write_prb(prb_path, probe_group)
        logging.info(f"Loading probe: {prb_path}")
        kilosort4_probe = load_probe(prb_path)

        # Find probe-specific or default Kilosort 4 settings.
        kilosort_settings_path = find_one(kilosort_settings_pattern, probe_id, none_ok=True)
        if kilosort_settings_path is None:
            logging.warning("Using default Kilosort 4 settings.")
            kilosort_settings = DEFAULT_SETTINGS
        else:
            logging.info(f"Loading Kilosort 4 settings from JSON: {kilosort_settings_path}")
            with open(kilosort_settings_path, 'r') as settings_in:
                kilosort_settings = json.load(settings_in)

        # Record the effective settings used for this probe.
        kilosort_settings["n_chan_bin"] = binary_channel_count
        effective_settings_path = Path(probe_results_path, f"{probe_id}-kilosort4-effective-settings.json")
        logging.info(f"Saving effective Kilosort 4 settings: {effective_settings_path}")
        with open(effective_settings_path, 'w') as settings_out:
            json.dump(kilosort_settings, settings_out)

        logging.info(f"Begin sorting for {probe_id}")
        run_kilosort(
            device=device,
            settings=kilosort_settings,
            filename=ab_bin_path,
            probe=kilosort4_probe,
            results_dir=probe_results_path
        )
        logging.info(f"Completed sorting for {probe_id}")

    logging.info(f"Completed sorting for {probe_count} probes.")
    if probe_count < 1:
        raise ValueError(f"Found no recordings matching probe ids: {probe_ids}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    set_up_logging()

    parser = ArgumentParser(description="Find one or more SpikeGLX recordings/probes and sort with Kilosort 4.")

    parser.add_argument(
        "--probe-ids",
        type=str,
        nargs="+",
        help="One or more probe ids to consider for sorting and for associating probes with Kilosort parameters. (default: %(default)s)",
        default=["imec0", "imec1"]
    )
    parser.add_argument(
        "--ap-meta-pattern",
        type=str,
        help="Glob pattern used to search for one or more SpikeGLX recordings/probes. (default: %(default)s)",
        default="**/*.ap.meta"
    )
    parser.add_argument(
        "--kilosort-settings-pattern",
        type=str,
        help="Glob pattern used to search for JSON files with Kilosort 4 settings. (default: %(default)s)",
        default="**/*-kilosort4-settings.json"
    )
    parser.add_argument(
        "--results-dir", "-r",
        type=str,
        help="Where to write output result files (can be distinct from the input dirs). (default: %(default)s)",
        default="results"
    )

    cli_args = parser.parse_args(argv)
    results_path = Path(cli_args.results_dir)
    try:
        find_probes_and_sort(
            cli_args.probe_ids,
            cli_args.ap_meta_pattern,
            cli_args.kilosort_settings_pattern,
            results_path
        )
    except:
        logging.error("Error running Kilosort 4.", exc_info=True)
        return -1


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
