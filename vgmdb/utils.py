from enum import Enum
import re
from abc import ABC
from lxml import etree
import datetime

import vgmdb


class VGMdbType(Enum):
    Album = 0
    Artist = 1
    Org = 2
    Product = 3
    Event = 4

    def __str__(self) -> str:
        return self.name.lower()

    @staticmethod
    def from_str(s: str) -> "VGMdbType":
        try:
            return VGMdbType[s.capitalize()]
        except KeyError:
            raise ValueError()

    @staticmethod
    def join() -> str:
        return "|".join([t.name.lower() for t in VGMdbType])


class Name:
    en: str | None = None
    ja: str | None = None
    ja_latn: str | None = None

    def __init__(
        self, en: str | None = None, ja: str | None = None, ja_latn: str | None = None
    ) -> None:
        self.en = en
        self.ja = ja
        self.ja_latn = ja_latn

    def __str__(self) -> str:
        return self.en or self.ja or self.ja_latn or ""

    @staticmethod
    def from_element(element: etree._Element) -> "Name":
        name = Name()
        if en := element.xpath('./span[@lang="en"]/text()'):
            name.en = en[0]
        elif en := element.xpath("./text()"):
            name.en = en[0]
        if ja := element.xpath('./span[@lang="ja"]/text()'):
            name.ja = ja[0]
        if ja_latn := element.xpath('./span[@lang="ja-Latn"]/text()'):
            name.ja_latn = ja_latn[0]
        return name

    def set_lang(self, lang: str, value: str) -> None:
        match lang:
            case "English":
                self.en = value
            case "Japanese":
                self.ja = value
            case "Romaji":
                self.ja_latn = value


class Link:
    type: VGMdbType
    id: int

    def __init__(self, type: VGMdbType, id: int) -> None:
        self.type = type
        self.id = id

    def __str__(self) -> str:
        return f"{self.type.name.lower()}/{self.id}"

    @staticmethod
    def from_url(url: str) -> "Link":
        if m := re.search(rf"(?P<type>{VGMdbType.join()})/(?P<id>\d+)", url):
            return Link(VGMdbType.from_str(m.group("type")), int(m.group("id")))
        elif m := re.search(rf"/search\?special=(?P<type>{VGMdbType.join()})", url):
            return Link(VGMdbType.from_str(m.group("type")), -1)
        else:
            raise ValueError(f"Invalid url: {url}")

    @staticmethod
    def from_element(element: etree._Element) -> "Link":
        if url := element.attrib.get("href"):
            return Link.from_url(url)
        else:
            raise ValueError("Invalid element")

    def full_url(self) -> str:
        return f"https://vgmdb.net/{self:s}"


class Picture:
    type: VGMdbType
    id: int
    ext_id: str

    def __init__(self, type: VGMdbType, id: int, ext_id: str) -> None:
        self.type = type
        self.id = id
        self.ext_id = ext_id

    def __str__(self) -> str:
        return f"{self.type}s/{f'{self.id:02}'[:-3:-1]}/{self.id}-{self.ext_id}"

    @staticmethod
    def from_url(url: str) -> "Picture":
        m = re.search(
            rf"(?P<type>{VGMdbType.join()})s/\d{{2}}/(?P<id>\d+)/\d+-(?P<ext_id>\w+)",
            url,
        )
        if m:
            return Picture(
                VGMdbType.from_str(m.group("type")),
                int(m.group("id")),
                m.group("ext_id"),
            )
        else:
            raise ValueError()

    def full_url(self) -> str:
        return f"https://media.vgm.io/{self}.jpg"

    def medium_url(self) -> str:
        return f"https://medium-media.vgm.io/{self}.jpg"

    def thumb_url(self) -> str:
        return f"https://thumb-media.vgm.io/{self}.jpg"


class Track:
    index: int
    title: Name
    length: datetime.timedelta | None
    subtracks: list["Track"]

    def __init__(self, index: int) -> None:
        self.index = index

    def __str__(self) -> str:
        return f"{self.index}. {self.title}"


class Tracklist:
    disc: int
    catalog: str | None
    type: str | None
    tracks: list[Track]
    length: datetime.timedelta | None
    label: list[str] | None

    def __init__(
        self,
        disc: int,
        catalog: str | None = None,
        type: str | None = None,
    ) -> None:
        self.disc = disc
        self.catalog = catalog
        self.type = type

    def __str__(self) -> str:
        return f"{self.disc:02} - {self.catalog or ''} - {self.type or ''}"

    @staticmethod
    def from_element(element: etree._Element) -> "Tracklist":
        return Tracklist(-1)


class VGMdbObject(ABC):
    type: VGMdbType
    id: int
    name: Name
    link: Link

    def __init__(self, id: int | str, name: str | Name | None = None) -> None:
        self.id = int(id)
        self.name = name if isinstance(name, Name) else Name(name)
        self.link = Link(self.type, self.id)

    def __str__(self) -> str:
        return self.name.en or self.name.ja or self.name.ja_latn or ""
    
    def get_detail(self) -> "VGMdbObject":
        new_object = vgmdb.VGMdb.get(self.id, self.type)
        self.__dict__.update(new_object.__dict__)
        return self


def parse_date(date: str) -> datetime.date | None:
    formats = ["%b %d, %Y", "%b %Y", "%Y"]
    for f in formats:
        try:
            return datetime.datetime.strptime(date, f).date()
        except ValueError:
            pass
    raise (ValueError(f"Invalid date: {date}"))


def parse_time(time: str) -> datetime.timedelta | None:
    split = time.split(":")
    t = 0
    for i in split:
        t = t * 60 + int(i)
    try:
        return datetime.timedelta(seconds=t)
    except ValueError:
        raise (ValueError(f"Invalid time: {time}"))
