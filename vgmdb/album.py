from .utils import (
    VGMdbObject,
    VGMdbType,
    Link,
    Name,
    Picture,
    Track,
    Tracklist,
    parse_date,
    parse_time,
)
import vgmdb

from enum import Enum
from lxml import etree
import datetime
import re


class Album(VGMdbObject):
    class Category(Enum):
        Game = "game"
        Animation = "anime"
        Publication = "print"
        Radio_Drama = "drama"
        Live_Action = "live"
        Tokusatsu_Puppetry = "toku"
        Multimedia_Franchise = "mult"
        Demo_Scene = "demo"
        Event = "event"
        Artist_Works = "works"
        Enclosure_Promo = "bonus"
        Doujin_Indie = "doujin"
        Delayed_Cancelled = "cancel"
        Bootleg = "bootleg"

    type: VGMdbType = VGMdbType.Album
    catalog: str | None = None
    category: Category | str | None = None
    child_album: bool = False
    release_date: datetime.date | None = None
    media_format: str
    picture: Picture | None = None

    # info
    barcode: int
    publish_format: str
    price: tuple[int, str]
    classification: list[str]
    label: list["vgmdb.Org"]
    publisher: list["vgmdb.Org"]
    manufacturer: list["vgmdb.Org"]
    distributor: list["vgmdb.Org"]
    phonographic_copyright: list["vgmdb.Org"]
    organizations: str

    # credits
    composer: list["vgmdb.Artist"]
    arranger: list["vgmdb.Artist"]
    performer: list["vgmdb.Artist"]
    lyricist: list["vgmdb.Artist"]
    other_staff: list["vgmdb.Artist"]

    # tracklist
    tracklist: list[Tracklist]

    # notes
    notes: str

    # covers
    covers: dict[str, Picture]

    # related albums
    related_albums: list["Album"]

    @staticmethod
    def from_table(element: etree._Element) -> "Album":
        link_element = element.xpath("./td[3]/a")[0]
        link = Link.from_element(link_element)
        album = Album(link.id)
        album.name = Name.from_element(link_element)
        album.link = link
        if category_attr := link_element.attrib.get("class"):
            album.category = Album.Category(category_attr.split("-")[1])
        if catalog := element.xpath("./td[1]/span/text()"):
            album.catalog = catalog[0]
        if element.xpath("./td[2]/img"):
            album.child_album = True
        if release_date := element.xpath("./td[4]/a/text()"):
            album.release_date = parse_date(release_date[0])
        if media_format := element.xpath("./td[5]/text()"):
            album.media_format = media_format[0]
        return album

    @staticmethod
    def from_page(page: etree._Element) -> "Album":
        link_ekelement = page.xpath("/html/head/link[1]")[0]
        link = Link.from_element(link_ekelement)
        album = Album(link.id)
        if name := page.xpath("//*[@id='innermain']/h1"):
            album.name = Name.from_element(name[0])
        if picture := page.xpath("/html/head/meta[@property='og:image']"):
            album.picture = Picture.from_url(picture[0].attrib["content"])
        if info_table := page.xpath("//div[@id='rightfloat']//table"):
            album.set_info(info_table[0])
        if credits_table := page.xpath("//div[@id='collapse_credits']//table"):
            album.set_credits(credits_table[0])
        if tracklist := page.xpath("//div[@id='tracklist']/../.."):
            album.set_tracklist(tracklist[0])
        if notes := page.xpath("//div[@id='notes']"):
            album.set_notes(notes[0])
        if album_stats := page.xpath(
            "//h3[text()='Album Stats']/../../following-sibling::div[1]/div"
        ):
            album.set_stats(album_stats[0])
        if covers := page.xpath("//div[@id='cover_gallery']"):
            album.set_covers(covers[0])
        if related_albums := page.xpath(
            "//h3[text()='Related Albums']/../../following-sibling::div[1]/span"
        ):
            album.set_related_albums(related_albums[0])
        return album

    def set_info(self, info_table: etree._Element) -> None:
        for row in info_table.xpath("./tr"):
            if row.getchildren() == []:
                continue
            label: str = row.xpath("./td[1]/span/b/text()")[0]
            value: etree._Element = row.xpath("./td[2]")[0]
            if label == "Catalog Number":
                self.catalog = value.xpath(".//text()")[0].strip()
            elif label == "Barcode":
                self.barcode = int(value.text.strip())
            elif label == "Release Date":
                self.release_date = parse_date(value.xpath(".//text()")[0].strip())
            elif label == "Publish Format":
                self.publish_format = value.text.strip()
            elif label == "Release Price":
                price: str = value.text.strip()
                if price.isdigit():
                    currency = value.xpath("./acronym/text()")[0].strip()
                    self.price = (int(price), currency)
                else:
                    self.price = (-1, "Unknown")
            elif label == "Media Format":
                self.media_format = value.text.strip()
            elif label == "Classification":
                self.classification = value.text.strip().split(", ")
            elif label == "Label":
                orgs = value.xpath("./a")
                self.label = [vgmdb.Org.from_element(org) for org in orgs]
            elif label == "Publisher":
                orgs = value.xpath("./a")
                self.publisher = [vgmdb.Org.from_element(org) for org in orgs]
            elif label == "Manufacturer":
                orgs = value.xpath("./a")
                self.manufacturer = [vgmdb.Org.from_element(org) for org in orgs]
            elif label == "Distributor":
                orgs = value.xpath("./a")
                self.distributor = [vgmdb.Org.from_element(org) for org in orgs]
            elif label == "Phonographic Copyright":
                orgs = value.xpath("./a")
                self.phonographic_copyright = [
                    vgmdb.Org.from_element(org) for org in orgs
                ]
            elif label == "Organizations":
                self.organizations = value.text.strip()
            elif label == "Exclusive Retailer":
                orgs = value.xpath("./a")
                self.exclusive_retailer = [vgmdb.Org.from_element(org) for org in orgs]
            elif label == "Marketer":
                orgs = value.xpath("./a")
                self.marketer = [vgmdb.Org.from_element(org) for org in orgs]
            else:
                try:
                    orgs = value.xpath("./a")
                    setattr(
                        self,
                        label.lower().replace(" ", "_"),
                        [vgmdb.Org.from_element(org) for org in orgs],
                    )
                except AttributeError:
                    raise ValueError(f"Unknown label {label}")
        if not hasattr(self, "media_format"):
            self.media_format = "CD"

    def set_credits(self, credits_table: etree._Element) -> None:
        for row in credits_table.xpath(".//tr"):
            label: str = row.xpath("./td[1]/span//text()")[0].lower()
            value: etree._Element = row.xpath("./td[2]")[0]
            if "compose" in label:
                if not hasattr(self, "composer"):
                    self.composer = []
                self.composer += vgmdb.Artist.from_mixed_td(value, label)
            elif "arrange" in label:
                if not hasattr(self, "arranger"):
                    self.arranger = []
                self.arranger += vgmdb.Artist.from_mixed_td(value, label)
            elif "performe" in label:
                if not hasattr(self, "performer"):
                    self.performer = []
                self.performer += vgmdb.Artist.from_mixed_td(value, label)
            elif "lyric" in label:
                if not hasattr(self, "lyricist"):
                    self.lyricist = []
                self.lyricist += vgmdb.Artist.from_mixed_td(value, label)
            else:
                if not hasattr(self, "other_staff"):
                    self.other_staff = []
                self.other_staff += vgmdb.Artist.from_mixed_td(value, label)

    def set_tracklist(self, tracklist_element: etree._Element) -> None:
        languages = {
            e.text: tracklist_element.xpath(
                f"./div[2]/div[@id='tracklist']/span[@id='{e.attrib['rel']}']"
            )[0]
            for e in tracklist_element.xpath("./div[1]/ul[@id='tlnav']/li/a")
        }
        self.tracklist = []
        for language, element in languages.items():
            discs = element.xpath("./table")
            for disc in discs:
                title = disc.xpath("./preceding-sibling::span/b/text()")[-1]
                group = re.match(
                    r"Disc (?P<num>\d+)(?: \((?P<type>.+)\))?(?: \[(?P<catalog>.+)\])?",
                    title,
                )
                if not group:
                    raise ValueError(f"Unknown title {title}")
                num = int(group.group("num"))
                if language == list(languages.keys())[0]:
                    type = group.group("type")
                    catalog = group.group("catalog")
                    if len(discs) == 1:
                        if type is None:
                            type = self.media_format
                        if catalog is None:
                            catalog = self.catalog
                    tracklist = Tracklist(num, catalog, type)
                    if label := disc.xpath(
                        "./preceding-sibling::span[@class='label']/text()"
                    ):
                        tracklist.label = label[-1].strip().split(", ")
                    if length := disc.xpath(
                        "./following-sibling::span[@class='time']/text()"
                    ):
                        tracklist.length = parse_time(length[0])
                    tracklist.tracks = []
                    self.tracklist.append(tracklist)
                else:
                    tracklist = self.tracklist[num - 1]
                index = 0
                for row in disc.xpath("./tr"):
                    if row.attrib.get("class") != "rolebit":
                        continue
                    if row.xpath("./td[1]/span/text()")[0].isdigit():
                        index = int(row.xpath("./td[1]/span/text()")[0])
                        if track := [i for i in tracklist.tracks if i.index == index]:
                            track[0].title.set_lang(
                                language, row.xpath("./td[2]/text()")[0].strip()
                            )
                        else:
                            track = Track(index)
                            track.title = Name()
                            track.title.set_lang(
                                language, row.xpath("./td[2]/text()")[0].strip()
                            )
                            if length := row.xpath("./td[3]/span/text()"):
                                track.length = parse_time(length[0])
                            tracklist.tracks.append(track)
                    else:
                        subindex = int(row.xpath("./td[2]/span/text()")[0])
                        track = tracklist.tracks[index - 1]
                        if not hasattr(track, "subtracks"):
                            track.subtracks = []
                        if subtrack := [
                            i for i in track.subtracks if i.index == subindex
                        ]:
                            subtrack[0].title.set_lang(
                                language, row.xpath("./td[2]/text()")[0].strip()
                            )
                        else:
                            subtrack = Track(subindex)
                            subtrack.title = Name()
                            subtrack.title.set_lang(
                                language, row.xpath("./td[2]/span")[0].tail.strip()
                            )
                            if length := row.xpath("./td[3]/span/text()"):
                                subtrack.length = parse_time(length[0])
                            track.subtracks.append(subtrack)

    def set_notes(self, notes_element: etree._Element) -> None:
        notes = notes_element.xpath(".//text()")
        self.notes = "\n".join(notes).strip()

    def set_stats(self, stats_element: etree._Element) -> None:
        category = stats_element.xpath(".//b[text()='Category']/../text()")[1].strip()
        if category in Album.Category.__members__:
            self.category = Album.Category.__members__[category]
        else:
            self.category = category

    def set_covers(self, covers_element: etree._Element) -> None:
        covers = covers_element.xpath(".//td/a")
        self.covers = {}
        for cover in covers:
            name = cover.xpath("./h4/text()")[0]
            href = cover.attrib["href"]
            picture = Picture.from_url(href)
            self.covers[name] = picture

    def set_related_albums(self, related_albums_element: etree._Element) -> None:
        related_albums = related_albums_element.xpath("./div")
        self.related_albums = []
        for related_album in related_albums:
            if link_element := related_album.xpath("./ul/li[1]/a"):
                link = Link.from_element(link_element[0])
                album = Album(link.id)
                album.name = Name.from_element(link_element[0])
                album.link = link
                if category_attr := link_element[0].attrib.get("class"):
                    album.category = Album.Category(category_attr.split("-")[1])
                if catalog := related_album.xpath("./ul/li[2]/span/text()")[0]:
                    album.catalog = catalog
                if release_date := related_album.xpath("./ul/li[3]/text()"):
                    album.release_date = parse_date(release_date[0])
                if picture := related_album.xpath("./div/div/@style"):
                    if picture[0].split("'")[1].endswith(".gif"):
                        album.picture = None
                    else:
                        album.picture = Picture.from_url(picture[0].split("'")[1])
                self.related_albums.append(album)
            elif link_element := related_album.xpath("./a"):
                link = Link.from_element(link_element[0])
                album = Album(link.id)
                album.name = Name.from_element(link_element[0])
                album.link = link
                if catalog := related_album.xpath("./span/text()")[0]:
                    album.catalog = catalog
                self.related_albums.append(album)
            else:
                raise ValueError("Unknown related album type")
