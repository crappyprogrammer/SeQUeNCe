from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..kernel.timeline import Timeline
    from ..components.interferometer import Interferometer

from .photon import Photon
from ..kernel.entity import Entity
from ..kernel.event import Event
from ..kernel.process import Process


class Switch(Entity):
    def __init__(self, name: str, timeline: "Timeline"):
        Entity.__init__(self, name, timeline)
        self.start_time = 0
        self.frequency = 0
        self.basis_list = []
        self.interferometer = None
        self.detector = None

    def init(self) -> None:
        pass

    def set_detector(self, detector: "Detector") -> None:
        self.detector = detector

    def set_interferometer(self, interferometer: "Interferometer") -> None:
        self.interferometer = interferometer

    def set_basis_list(self, basis_list: "List[int]", start_time: int, frequency: int) -> None:
        self.basis_list = basis_list
        self.start_time = start_time
        self.frequency = frequency

    def get(self, photon: "Photon") -> None:
        index = int((self.timeline.now() - self.start_time) * self.frequency * 1e-12)
        if index < 0 or index >= len(self.basis_list):
            return

        if self.basis_list[index] == 0:
            receiver = self.detector
            # check if receiver is detector, if we're using time bin, and if the photon is "late" to schedule measurement
            assert photon.encoding_type["name"] == "time_bin"
            if Photon.measure(photon.encoding_type["bases"][0], photon):
                time = self.timeline.now() + photon.encoding_type["bin_separation"]
                process = Process(receiver, "get", [])
                event = Event(time, process)
                self.timeline.schedule(event)
            else:
                time = self.timeline.now()
                process = Process(receiver, "get", [])
                event = Event(time, process)
                self.timeline.schedule(event)
        else:
            receiver = self.interferometer
            time = self.timeline.now()
            process = Process(receiver, "get", [photon])
            event = Event(time, process)
            self.timeline.schedule(event)
