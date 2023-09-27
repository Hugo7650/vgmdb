


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
    """VGMdb API client.
    """
    session = requests.Session()

    @staticmethod
    def get(id: int, type: VGMdbType) -> VGMdbObject | None:
        """Get an object from VGMdb.

        Args:
            id (int): ID of the object.
            type (VGMdbType): Type of the object.

        Returns:
            VGMdbObject | None: The object if found, None otherwise.
        """
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
        """Get an album from VGMdb.

        Args:
            id (int): ID of the album.

        Returns:
            Album | None: The album if found, None otherwise.
        """
        return cast(Album | None, VGMdb.get(id, VGMdbType.Album))

    @staticmethod
    def get_artist(id: int) -> Artist | None:
        """Get an artist from VGMdb.

        Args:
            id (int): ID of the artist.

        Returns:
            Artist | None: The artist if found, None otherwise.
        """
        return cast(Artist | None, VGMdb.get(id, VGMdbType.Artist))

    @staticmethod
    def get_event(id: int) -> Event | None:
        """Get an event from VGMdb.

        Args:
            id (int): ID of the event.

        Returns:
            Event | None: The event if found, None otherwise.
        """
        return cast(Event | None, VGMdb.get(id, VGMdbType.Event))

    @staticmethod
    def get_org(id: int) -> Org | None:
        """Get an organization from VGMdb.

        Args:
            id (int): ID of the organization.

        Returns:
            Org | None: The organization if found, None otherwise.
        """
        return cast(Org | None, VGMdb.get(id, VGMdbType.Org))

    @staticmethod
    def get_product(id: int) -> Product | None:
        """Get a product from VGMdb.

        Args:
            id (int): ID of the product.

        Returns:
            Product | None: The product if found, None otherwise.
        """
        return cast(Product | None, VGMdb.get(id, VGMdbType.Product))

    @staticmethod
    def search(query: str, type: VGMdbType | None = None) -> list[VGMdbObject]:
        """Search for objects on VGMdb.

        Args:
            query (str): The search query.
            type (VGMdbType | None, optional): The type of objects to search for. Defaults to None.

        Returns:
            list[VGMdbObject]: The list of objects found.
        """
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
        """Parse a search page.

        Args:
            page (etree._Element): The page to parse.
            type (VGMdbType): The type of objects to search for.

        Returns:
            list[VGMdbObject]: The list of objects found.
        """
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
        """Search for albums on VGMdb.

        Args:
            query (str): The search query.

        Returns:
            list[Album]: The list of albums found.
        """
        result = VGMdb.search(query, VGMdbType.Album)
        return [i for i in result if isinstance(i, Album)]

    @staticmethod
    def search_artists(query: str) -> list[Artist]:
        """Search for artists on VGMdb.

        Args:
            query (str): The search query.

        Returns:
            list[Artist]: The list of artists found.
        """
        result = VGMdb.search(query, VGMdbType.Artist)
        return [i for i in result if isinstance(i, Artist)]

    @staticmethod
    def search_events(query: str) -> list[Event]:
        """Search for events on VGMdb.

        Args:
            query (str): The search query.

        Returns:
            list[Event]: The list of events found.
        """
        result = VGMdb.search(query, VGMdbType.Event)
        return [i for i in result if isinstance(i, Event)]

    @staticmethod
    def search_orgs(query: str) -> list[Org]:
        """Search for organizations on VGMdb.

        Args:
            query (str): The search query.

        Returns:
            list[Org]: The list of organizations found.
        """
        result = VGMdb.search(query, VGMdbType.Org)
        return [i for i in result if isinstance(i, Org)]

    @staticmethod
    def search_products(query: str) -> list[Product]:
        """Search for products on VGMdb.

        Args:
            query (str): The search query.

        Returns:
            list[Product]: The list of products found.
        """
        result = VGMdb.search(query, VGMdbType.Product)
        return [i for i in result if isinstance(i, Product)]

    @staticmethod
    def set_session(session: requests.Session) -> None:
        """Set the session to use for requests.

        Args:
            session (requests.Session): The session to use.
        """
        VGMdb.session = session

    @staticmethod
    def set_cookies(cookies: dict[str, str]) -> None:
        """Set the cookies to use for requests.

        Args:
            cookies (dict[str, str]): The cookies to use.
        """
        VGMdb.session.cookies.update(cookies)

    @staticmethod
    def set_proxy(proxy: str) -> None:
        """Set the proxy to use for requests.

        Args:
            proxy (str): The proxy to use.
        """
        VGMdb.session.proxies.update({"https": proxy})
