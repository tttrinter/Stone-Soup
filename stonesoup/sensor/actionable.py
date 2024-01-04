from abc import ABC

from ..sensormanager.actionable import Actionable


class SensorActionable(Actionable):
    """Sensor Actionable base class

    Base class for actionable sensors which has all the functionality of base
    :class:`~.Actionable` class, with additional sensor-specific features.
    """
    # Word better and check if :class: part is right

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
