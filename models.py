from dataclasses import dataclass
from typing import List

from util import merge_distributions


@dataclass
class Response:
    true_azimuth: int
    response_azimuth: int
    azimuth_choices: List[int]
    response_delay_ms: int

    @property
    def is_correct(self):
        return self.response_azimuth == self.true_azimuth

    @property
    def error(self):
        return self.response_azimuth - self.true_azimuth

    @property
    def true_index(self):
        return self.azimuth_choices.index(self.true_azimuth)

    @property
    def response_index(self):
        return self.azimuth_choices.index(self.response_azimuth)


@dataclass
class Block:
    center_azimuth: int
    responses: List[Response]

    @property
    def num_responses(self):
        return len(self.responses)

    @property
    def num_correct_responses(self):
        return len([r for r in self.responses if r.is_correct])

    @property
    def fraction_correct_responses(self):
        return self.num_correct_responses / self.num_responses

    @property
    def average_error(self):
        errors = []
        for response in self.responses:
            error = abs(response.error)
            errors.append(error)
        return sum(errors) / len(errors)

    @property
    def error_distribution(self):
        errors = {}
        for response in self.responses:
            error = response.error
            if not errors.get(error):
                errors[error] = 0
            errors[error] += 1
        return errors


@dataclass
class Participant:
    version: str
    user_agent: str
    compensation: int
    slowdown: int
    blocks: List[Block]

    def _get_blocks(self, kind=None):
        if kind == "left":
            return [b for b in self.blocks if b.center_azimuth < 0]
        elif kind == "right":
            return [b for b in self.blocks if b.center_azimuth > 0]
        elif kind == "center":
            return [b for b in self.blocks if b.center_azimuth == 0]
        return self.blocks

    def get_responses(self, kind=None):
        blocks = self._get_blocks(kind)
        return [response for block in blocks for response in block.responses]

    @property
    def fraction_correct_responses(self):
        total = 0
        correct = 0
        for block in self._get_blocks():
            total += block.num_responses
            correct += block.num_correct_responses
        return correct / total

    @property
    def average_error(self):
        errors = []
        for block in self._get_blocks():
            for response in block.responses:
                error = response.error
                errors.append(error)
        return sum(errors) / len(errors)

    @property
    def error_distribution(self):
        return merge_distributions([block.error_distribution for block in self._get_blocks()])