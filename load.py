from os import listdir, path
from csv import DictReader

from models import Response, Block, Participant

invalid_prolific_pids = [
    "5feb726715b59bbd3c904409",  # Wrote in to say semicolon was broken
    "5bc2e0ec4f3bfd00012e97b5",  # Obviously phoning it in
    "5e328fc0a7365325cc819dae", # Repeat runs > 10 of same choice
]

def get_data_file_paths():
    data_dir = path.normpath(path.join(__file__, "..", "data"))
    children = [path.join(data_dir, child) for child in listdir(data_dir)]
    return [child for child in children if path.isfile(child) and child.endswith(".csv")]


def get_participant_for_file(path):
    with open(path, "r") as data_file:
        reader = DictReader(data_file)
        if "version" not in reader.fieldnames:
            return None
        blocks = []
        prolific_pid = None
        slowdown = None
        keyset = None
        compensation = None
        user_agent = None
        current_block_responses = []
        current_block_center = None
        version = None
        for row in reader:
            prolific_pid = row.get("prolificPid")
            if prolific_pid in invalid_prolific_pids:
                return None
            if row["trial_type"] == "keyset-select":
                keyset = row.get("chosenKeyset")
            if row["trial_type"] == "block-bookend" and len(current_block_responses) == 20:
                next_block = Block(
                    center_azimuth=current_block_center, responses=current_block_responses
                )
                blocks.append(next_block)
                current_block_responses = []
            if row["trial_type"] == "echo-presentation":
                choices = list(map(int, row.get("choices").split(",")))
                current_block_center = choices[2]
                slowdown = int(row.get("slowdown"))
                compensation = int(row.get("compensation"))
                true_azimuth = row.get("azimuth")
                user_agent = row.get("userAgent")
                version = row.get("version")
                response_azimuth = row.get("responseAzimuth")
                response_delay = row.get("responseDelay")
                if true_azimuth and response_azimuth:
                    response = Response(
                        true_azimuth=int(true_azimuth),
                        response_azimuth=int(response_azimuth),
                        azimuth_choices=choices,
                        response_delay_ms=int(response_delay),
                    )
                    current_block_responses.append(response)
        if len(blocks) == 6 and slowdown and compensation and version and prolific_pid:
            return Participant(
                version=version,
                user_agent=user_agent,
                compensation=compensation,
                slowdown=slowdown,
                blocks=blocks,
                keyset=keyset,
                prolific_pid=prolific_pid,
            )
    return None


_participants = [get_participant_for_file(file) for file in get_data_file_paths()]


def get_participant_data(
    slowdown: int, compensation: int, version: str = "v1-up-stims", keyset=None
):
    return [
        p
        for p in _participants
        if (
            p
            and p.slowdown == slowdown
            and p.compensation == compensation
            and p.version == version
            and (keyset == None or keyset == p.keyset)
        )
    ]