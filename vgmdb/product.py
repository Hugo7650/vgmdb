from .utils import VGMdbObject, VGMdbType, Name, Link, parse_date

from enum import Enum
from lxml import etree
import datetime


class Product(VGMdbObject):
    class Category(Enum):
        Game = "#CEFFFF"
        Animation = "yellowgreen"
        Radio_Drama = "silver"
        Publication = "white"
        Goods = "violet"
        Live_Action = "#0FFFFF"
        Tokusatsu_Puppetry = "pink"
        Multimedia_Franchise = "#D2B48C"
        Other = "#00BFFF"
        Franchise = "yellow"
        Meta_franchise = "orange"

    type: VGMdbType = VGMdbType.Product
    category: Category | None = None
    release_date: datetime.date | None = None

    @staticmethod
    def from_table(element: etree._Element) -> "Product":
        link_element = element.xpath("./td[1]/a")[0]
        link = Link.from_element(link_element)
        product = Product(link.id)
        product.name = Name.from_element(link_element)
        color = link_element[0].xpath("./span")[0].attrib["style"].split(":")[1].strip()
        product.category = Product.Category(color)
        if release_date := element.xpath("./td[2]/a/text()"):
            product.release_date = parse_date(release_date[0])
        return product

    @staticmethod
    def from_page(page) -> "Product":
        return Product(-1)  # TODO
