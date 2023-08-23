from .utils import VGMdbObject, VGMdbType, Name, Link

from lxml import etree


class Org(VGMdbObject):
    type: VGMdbType = VGMdbType.Org
    aliases: list[str] | None

    @staticmethod
    def from_table(element: etree._Element) -> "Org":
        link_element = element.xpath("./td/a")[0]
        link = Link.from_element(link_element)
        org = Org(link.id)
        org.name = Name.from_element(link_element)
        if aliases := element.xpath("./td/span/text()"):
            org.aliases = list(map(lambda x: x.strip(), aliases[0].split("/")))[1:]
        return org

    @staticmethod
    def from_page(page) -> "Org":
        return Org(-1)  # TODO

    @staticmethod
    def from_element(element: etree._Element) -> "Org":
        link = Link.from_element(element)
        org = Org(link.id)
        org.name = Name.from_element(element)
        if aliases := element.xpath("./td/span/text()"):
            org.aliases = list(map(lambda x: x.strip(), aliases[0].split("/")))[1:]
        return org
