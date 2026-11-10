from __future__ import annotations


def position_accuracy(truths: list[str], predictions: list[str]) -> list[float]:
    if not truths or len(truths) != len(predictions):
        raise ValueError("truths and predictions must be non-empty and equally long")
    digit_count = len(truths[0])
    hits = [0] * digit_count
    for truth, prediction in zip(truths, predictions):
        for position in range(digit_count):
            hits[position] += truth[position] == prediction[position]
    return [hit / len(truths) for hit in hits]


def reading_accuracy(truths: list[str], predictions: list[str]) -> float:
    if not truths or len(truths) != len(predictions):
        raise ValueError("truths and predictions must be non-empty and equally long")
    return sum(truth == prediction for truth, prediction in zip(truths, predictions)) / len(truths)
