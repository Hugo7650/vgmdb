from .utils import VGMdbObject, VGMdbType

from lxml import etree


class Event(VGMdbObject):
    type: VGMdbType = VGMdbType.Event

    @staticmethod
    def from_table(element: etree._Element) -> "Event":
        return Event(-1)  # TODO

    @staticmethod
    def from_page(page) -> "Event":
        return Event(-1)  # TODO
