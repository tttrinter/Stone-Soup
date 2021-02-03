# -*- coding: utf-8 -*-
import datetime

import pytest

from ..tracktotrack import TrackToTrack, TrackToTruth, TrackIDbased
from ...types.state import State
from ...types.track import Track
from ...types.groundtruth import GroundTruthPath, GroundTruthState


@pytest.fixture
def tracks():
    start_time = datetime.datetime(2019, 1, 1, 14, 0, 0)

    tracks = [Track(states=[
        State(state_vector=[[i], [i]],
              timestamp=start_time + datetime.timedelta(seconds=i))
        for i in range(10)])]

    # 2nd track should be associated with track1 from the second timestamp to
    # the 6th
    tracks.append(Track(states=[
        State(state_vector=[[20], [20]],
              timestamp=start_time)]
        + [State(state_vector=[[i + 2], [i + 2]],
                 timestamp=start_time + datetime.timedelta(seconds=i))
           for i in range(1, 7)]))

    # 3rd is at a different time so should not associate with anything
    tracks.append(Track(states=[
        State(state_vector=[[i], [i]],
              timestamp=start_time + datetime.timedelta(seconds=i + 20))
        for i in range(10)]))

    # 4th is outside the association threshold
    tracks.append(Track(states=[
        State(state_vector=[[i + 20], [i + 20]],
              timestamp=start_time + datetime.timedelta(seconds=i))
        for i in range(10)]))

    return tracks


def test_euclidiantracktotrack(tracks):
    associator = TrackToTrack(
        association_threshold=10,
        consec_pairs_confirm=3,
        consec_misses_end=2)
    start_time = datetime.datetime(2019, 1, 1, 14, 0, 0)

    association_set = associator.associate_tracks({tracks[0], tracks[2]},
                                                  {tracks[1], tracks[3]})

    assert len(association_set.associations) == 1
    assoc = list(association_set.associations)[0]
    assert set(assoc.objects) == {tracks[0], tracks[1]}
    assert assoc.time_range.start_timestamp \
        == start_time + datetime.timedelta(seconds=1)
    assert assoc.time_range.end_timestamp \
        == start_time + datetime.timedelta(seconds=6)


def test_euclidiantracktotruth(tracks):
    associator = TrackToTruth(
        association_threshold=10,
        consec_pairs_confirm=3,
        consec_misses_end=2)
    start_time = datetime.datetime(2019, 1, 1, 14, 0, 0)

    association_set = associator.associate_tracks(
        truth_set={tracks[0]}, tracks_set={tracks[2], tracks[1], tracks[3]})

    assert len(association_set.associations) == 1
    assoc = list(association_set.associations)[0]
    assert set(assoc.objects) == {tracks[0], tracks[1]}
    assert assoc.time_range.start_timestamp == start_time + datetime.timedelta(
        seconds=1)
    assert assoc.time_range.end_timestamp == start_time + datetime.timedelta(
        seconds=6)


def test_trackidbased():
    associator = TrackIDbased()
    start_time = datetime.datetime(2019, 1, 1, 14, 0, 0)

    tracks = [Track(states=[State(state_vector=[[i]],
                                  timestamp=start_time),
                            State(state_vector=[[i]],
                                  timestamp=start_time + datetime.timedelta(
                                     seconds=1))],
                    id=f"id{i}")
              for i in range(0, 5)]
    truths = [GroundTruthPath(
        states=[GroundTruthState(state_vector=[[i+0.5]],
                                 timestamp=start_time),
                GroundTruthState(state_vector=[[i+0.5]],
                                 timestamp=start_time + datetime.timedelta(seconds=1))],
        id=f"id{i}")
        for i in range(0, 5)]

    association_set = associator.associate_tracks(tracks, truths)
    assert len(association_set.associations) == 5

    assoc = list(association_set.associations)[0]
    assoc_track = assoc.objects[0]
    assoc_truth = assoc.objects[1]
    assert assoc_track.id == assoc_truth.id
