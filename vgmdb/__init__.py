from .utils import VGMdbObject, VGMdbType
from .album import Album
from .artist import Artist
from .event import Event
from .org import Org
from .product import Product

import requests
from lxml import etree
from typing import cast


class VGMdb:
    session = requests.Session()

    @staticmethod
    def get(id: int, type: VGMdbType) -> VGMdbObject | None:
        url = f"https://vgmdb.net/{type}/{id}"
        response = VGMdb.session.get(url)
        response.raise_for_status()
        page = etree.HTML(response.text, etree.HTMLParser())
        if page.xpath("//h1/text()")[0] == "System Message":
            return None
        match type:
            case VGMdbType.Album:
                return Album.from_page(page)
            case VGMdbType.Artist:
                return Artist.from_page(page)
            case VGMdbType.Event:
                return Event.from_page(page)
            case VGMdbType.Org:
                return Org.from_page(page)
            case VGMdbType.Product:
                return Product.from_page(page)

    @staticmethod
    def get_album(id: int) -> Album | None:
        return cast(Album | None, VGMdb.get(id, VGMdbType.Album))

    @staticmethod
    def get_artist(id: int) -> Artist | None:
        return cast(Artist | None, VGMdb.get(id, VGMdbType.Artist))

    @staticmethod
    def get_event(id: int) -> Event | None:
        return cast(Event | None, VGMdb.get(id, VGMdbType.Event))

    @staticmethod
    def get_org(id: int) -> Org | None:
        return cast(Org | None, VGMdb.get(id, VGMdbType.Org))

    @staticmethod
    def get_product(id: int) -> Product | None:
        return cast(Product | None, VGMdb.get(id, VGMdbType.Product))

    @staticmethod
    def search(query: str, type: VGMdbType | None = None) -> list[VGMdbObject]:
        url = f"https://vgmdb.net/search?q={query}"
        if type:
            url += f"&type={type}"
        response = VGMdb.session.get(url)
        response.raise_for_status()
        page = etree.HTML(response.text, etree.HTMLParser())
        if type:
            return VGMdb.parse_search(page, type)
        else:
            result = []
            for t in VGMdbType:
                result += VGMdb.parse_search(page, t)
            return result

    @staticmethod
    def parse_search(page: etree._Element, type: VGMdbType) -> list[VGMdbObject]:
        result = []
        xpath = f'//div[@id="{type}results"]/table/tbody/tr'
        match type:
            case VGMdbType.Album:
                result += [Album.from_table(i) for i in page.xpath(xpath)]
            case VGMdbType.Artist:
                result += [Artist.from_table(i) for i in page.xpath(xpath)]
            case VGMdbType.Event:
                result += [Event.from_table(i) for i in page.xpath(xpath)]
            case VGMdbType.Org:
                result += [Org.from_table(i) for i in page.xpath(xpath)]
            case VGMdbType.Product:
                result += [Product.from_table(i) for i in page.xpath(xpath)]
        return result

    @staticmethod
    def search_albums(query: str) -> list[Album]:
        result = VGMdb.search(query, VGMdbType.Album)
        return [i for i in result if isinstance(i, Album)]

    @staticmethod
    def search_artists(query: str) -> list[Artist]:
        result = VGMdb.search(query, VGMdbType.Artist)
        return [i for i in result if isinstance(i, Artist)]

    @staticmethod
    def search_events(query: str) -> list[Event]:
        result = VGMdb.search(query, VGMdbType.Event)
        return [i for i in result if isinstance(i, Event)]

    @staticmethod
    def search_orgs(query: str) -> list[Org]:
        result = VGMdb.search(query, VGMdbType.Org)
        return [i for i in result if isinstance(i, Org)]

    @staticmethod
    def search_products(query: str) -> list[Product]:
        result = VGMdb.search(query, VGMdbType.Product)
        return [i for i in result if isinstance(i, Product)]

    @staticmethod
    def set_session(session: requests.Session) -> None:
        VGMdb.session = session

    @staticmethod
    def set_cookies(cookies: dict[str, str]) -> None:
        VGMdb.session.cookies.update(cookies)

    @staticmethod
    def set_proxy(proxy: str) -> None:
        VGMdb.session.proxies.update({"https": proxy})
