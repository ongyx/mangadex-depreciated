# coding: utf-8

"""
    MangaDex API

    MangaDex is an ad-free manga reader offering high-quality images!  This document details our API as it is right now. It is in no way a promise to never change it, although we will endeavour to publicly notify any major change.  # Authentication  You can login with the `/auth/login` endpoint. On success, it will return a JWT that remains valid for 15 minutes along with a session token that allows refreshing without re-authenticating for 1 month.  # Rate limits  The API enforces rate-limits to protect our servers against malicious and/or mistaken use. The API keeps track of the requests on an IP-by-IP basis. Hence, if you're on a VPN, proxy or a shared network in general, the requests of other users on this network might affect you.  At first, a **global limit of 5 requests per second per IP address** is in effect.  > This limit is enforced across multiple load-balancers, and thus is not an exact value but rather a lower-bound that we guarantee. The exact value will be somewhere in the range `[5, 5*n]` (with `n` being the number of load-balancers currently active). The exact value within this range will depend on the current traffic patterns we are experiencing.  On top of this, **some endpoints are further restricted** as follows:  | Endpoint                           | Requests per time period    | Time period in minutes | |------------------------------------|--------------------------   |------------------------| | `POST   /account/create`           | 1                           | 60                     | | `GET    /account/activate/{code}`  | 30                          | 60                     | | `POST   /account/activate/resend`  | 5                           | 60                     | | `POST   /account/recover`          | 5                           | 60                     | | `POST   /account/recover/{code}`   | 5                           | 60                     | | `POST   /auth/login`               | 30                          | 60                     | | `POST   /auth/refresh`             | 30                          | 60                     | | `POST   /author`                   | 10                          | 60                     | | `PUT    /author`                   | 10                          | 1                      | | `DELETE /author/{id}`              | 10                          | 10                     | | `POST   /captcha/solve`            | 10                          | 10                     | | `POST   /chapter/{id}/read`        | 300                         | 10                     | | `PUT    /chapter/{id}`             | 10                          | 1                      | | `DELETE /chapter/{id}`             | 10                          | 1                      | | `POST   /manga`                    | 10                          | 60                     | | `PUT    /manga/{id}`               | 10                          | 60                     | | `DELETE /manga/{id}`               | 10                          | 10                     | | `POST   /cover`                    | 10                          | 1                      | | `PUT    /cover/{id}`               | 10                          | 1                      | | `DELETE /cover/{id}`               | 10                          | 10                     | | `POST   /group`                    | 10                          | 60                     | | `PUT    /group/{id}`               | 10                          | 1                      | | `DELETE /group/{id}`               | 10                          | 10                     | | `GET    /at-home/server/{id}`      | 60                          | 1                      |  Calling these endpoints will further provide details via the following headers about your remaining quotas:  | Header                    | Description                                                                 | |---------------------------|-----------------------------------------------------------------------------| | `X-RateLimit-Limit`       | Maximal number of requests this endpoint allows per its time period         | | `X-RateLimit-Remaining`   | Remaining number of requests within your quota for the current time period  | | `X-RateLimit-Retry-After` | Timestamp of the end of the current time period, as UNIX timestamp          |  # Captchas  Some endpoints may require captchas to proceed, in order to slow down automated malicious traffic. Legitimate users might also be affected, based on the frequency of write requests or due certain endpoints being particularly sensitive to malicious use, such as user signup.  Once an endpoint decides that a captcha needs to be solved, a 403 Forbidden response will be returned, with the error code `captcha_required_exception`. The sitekey needed for recaptcha to function is provided in both the `X-Captcha-Sitekey` header field, as well as in the error context, specified as `siteKey` parameter.  The captcha result of the client can either be passed into the repeated original request with the `X-Captcha-Result` header or alternatively to the `POST /captcha/solve` endpoint. The time a solved captcha is remembered varies across different endpoints and can also be influenced by individual client behavior.  Authentication is not required for the `POST /captcha/solve` endpoint, captchas are tracked both by client ip and logged in user id. If you are logged in, you want to send the session token along, so you validate the captcha for your client ip and user id at the same time, but it is not required.  # Reading a chapter using the API  ## Retrieving pages from the MangaDex@Home network  A valid [MangaDex@Home network](https://mangadex.network) page URL is in the following format: `{server-specific base url}/{temporary access token}/{quality mode}/{chapter hash}/{filename}`  There are currently 2 quality modes: - `data`: Original upload quality - `data-saver`: Compressed quality  Upon fetching a chapter from the API, you will find 4 fields necessary to compute MangaDex@Home page URLs:  | Field                        | Type     | Description                       | |------------------------------|----------|-----------------------------------| | `.data.id`                   | `string` | API Chapter ID                    | | `.data.attributes.hash`      | `string` | MangaDex@Home Chapter Hash        | | `.data.attributes.data`      | `array`  | data quality mode filenames       | | `.data.attributes.dataSaver` | `array`  | data-saver quality mode filenames |  Example ```json GET /chapter/{id}  {   ...,   \"data\": {     \"id\": \"e46e5118-80ce-4382-a506-f61a24865166\",     ...,     \"attributes\": {       ...,       \"hash\": \"e199c7d73af7a58e8a4d0263f03db660\",       \"data\": [         \"x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png\",         ...       ],       \"dataSaver\": [         \"x1-ab2b7c8f30c843aa3a53c29bc8c0e204fba4ab3e75985d761921eb6a52ff6159.jpg\",         ...       ]     }   } } ```  From this point you miss only the base URL to an assigned MangaDex@Home server for your client and chapter. This is retrieved via a `GET` request to `/at-home/server/{ chapter .data.id }`.  Example: ```json GET /at-home/server/e46e5118-80ce-4382-a506-f61a24865166  {   \"baseUrl\": \"https://abcdefg.hijklmn.mangadex.network:12345/some-token\" } ```  The full URL is the constructed as follows ``` { server .baseUrl }/{ quality mode }/{ chapter .data.attributes.hash }/{ chapter .data.attributes.{ quality mode }.[*] }  Examples  data quality: https://abcdefg.hijklmn.mangadex.network:12345/some-token/data/e199c7d73af7a58e8a4d0263f03db660/x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png        base url: https://abcdefg.hijklmn.mangadex.network:12345/some-token   quality mode: data   chapter hash: e199c7d73af7a58e8a4d0263f03db660       filename: x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png   data-saver quality: https://abcdefg.hijklmn.mangadex.network:12345/some-token/data-saver/e199c7d73af7a58e8a4d0263f03db660/x1-ab2b7c8f30c843aa3a53c29bc8c0e204fba4ab3e75985d761921eb6a52ff6159.jpg        base url: https://abcdefg.hijklmn.mangadex.network:12345/some-token   quality mode: data-saver   chapter hash: e199c7d73af7a58e8a4d0263f03db660       filename: x1-ab2b7c8f30c843aa3a53c29bc8c0e204fba4ab3e75985d761921eb6a52ff6159.jpg ```  If the server you have been assigned fails to serve images, you are allowed to call the `/at-home/server/{ chapter id }` endpoint again to get another server.  Whether successful or not, **please do report the result you encountered as detailed below**. This is so we can pull the faulty server out of the network.  ## Report  In order to keep track of the health of the servers in the network and to improve the quality of service and reliability, we ask that you call the MangaDex@Home report endpoint after each image you retrieve, whether successfully or not.  It is a `POST` request against `https://api.mangadex.network/report` and expects the following payload with our example above:  | Field                       | Type       | Description                                                                         | |-----------------------------|------------|-------------------------------------------------------------------------------------| | `url`                       | `string`   | The full URL of the image                                                           | | `success`                   | `boolean`  | Whether the image was successfully retrieved                                        | | `cached `                   | `boolean`  | `true` iff the server returned an `X-Cache` header with a value starting with `HIT` | | `bytes`                     | `number`   | The size in bytes of the retrieved image                                            | | `duration`                  | `number`   | The time in miliseconds that the complete retrieval (not TTFB) of this image took   |  Examples herafter.  **Success:** ```json POST https://api.mangadex.network/report Content-Type: application/json  {   \"url\": \"https://abcdefg.hijklmn.mangadex.network:12345/some-token/data/e199c7d73af7a58e8a4d0263f03db660/x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png\",   \"success\": true,   \"bytes\": 727040,   \"duration\": 235,   \"cached\": true } ```  **Failure:** ```json POST https://api.mangadex.network/report Content-Type: application/json  {  \"url\": \"https://abcdefg.hijklmn.mangadex.network:12345/some-token/data/e199c7d73af7a58e8a4d0263f03db660/x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png\",  \"success\": false,  \"bytes\": 25,  \"duration\": 235,  \"cached\": false } ```  While not strictly necessary, this helps us monitor the network's healthiness, and we appreciate your cooperation towards this goal. If no one reports successes and failures, we have no way to know that a given server is slow/broken, which eventually results in broken image retrieval for everyone.  # Retrieving Covers from the API  ## Construct Cover URLs  ### Source (original/best quality)  `https://uploads.mangadex.org/covers/{ manga.id }/{ cover.filename }`<br/> The extension can be png, jpeg or gif.  Example: `https://uploads.mangadex.org/covers/8f3e1818-a015-491d-bd81-3addc4d7d56a/4113e972-d228-4172-a885-cb30baffff97.jpg`  ### <=512px wide thumbnail  `https://uploads.mangadex.org/covers/{ manga.id }/{ cover.filename }.512.jpg`<br/> The extension is always jpg.  Example: `https://uploads.mangadex.org/covers/8f3e1818-a015-491d-bd81-3addc4d7d56a/4113e972-d228-4172-a885-cb30baffff97.jpg.512.jpg`  ### <=256px wide thumbnail  `https://uploads.mangadex.org/covers/{ manga.id }/{ cover.filename }.256.jpg`<br/> The extension is always jpg.  Example: `https://uploads.mangadex.org/covers/8f3e1818-a015-491d-bd81-3addc4d7d56a/4113e972-d228-4172-a885-cb30baffff97.jpg.256.jpg`  ## ℹ️ Where to find Cover filename ?  Look at the [Get cover operation](#operation/get-cover) endpoint to get Cover information. Also, if you get a Manga resource, you'll have, if available a `covert_art` relationship which is the main cover id.  # Static data  ## Manga publication demographic  | Value            | Description               | |------------------|---------------------------| | shounen          | Manga is a Shounen        | | shoujo           | Manga is a Shoujo         | | josei            | Manga is a Josei          | | seinen           | Manga is a Seinen         |  ## Manga status  | Value            | Description               | |------------------|---------------------------| | ongoing          | Manga is still going on   | | completed        | Manga is completed        | | hiatus           | Manga is paused           | | cancelled        | Manga has been cancelled  |  ## Manga reading status  | Value            | |------------------| | reading          | | on_hold          | | plan\\_to\\_read   | | dropped          | | re\\_reading      | | completed        |  ## Manga content rating  | Value            | Description               | |------------------|---------------------------| | safe             | Safe content              | | suggestive       | Suggestive content        | | erotica          | Erotica content           | | pornographic     | Pornographic content      |  ## CustomList visibility  | Value            | Description               | |------------------|---------------------------| | public           | CustomList is public      | | private          | CustomList is private     |  ## Relationship types  | Value            | Description                    | |------------------|--------------------------------| | manga            | Manga resource                 | | chapter          | Chapter resource               | | cover_art        | A Cover Art for a manga `*`    | | author           | Author resource                | | artist           | Author resource (drawers only) | | scanlation_group | ScanlationGroup resource       | | tag              | Tag resource                   | | user             | User resource                  | | custom_list      | CustomList resource            |  `*` Note, that on manga resources you get only one cover_art resource relation marking the primary cover if there are more than one. By default this will be the latest volume's cover art. If you like to see all the covers for a given manga, use the cover search endpoint for your mangaId and select the one you wish to display.  ## Manga links data  In Manga attributes you have the `links` field that is a JSON object with some strange keys, here is how to decode this object:  | Key   | Related site  | URL                                                                                           | URL details                                                    | |-------|---------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------| | al    | anilist       | https://anilist.co/manga/`{id}`                                                               | Stored as id                                                   | | ap    | animeplanet   | https://www.anime-planet.com/manga/`{slug}`                                                   | Stored as slug                                                 | | bw    | bookwalker.jp | https://bookwalker.jp/`{slug}`                                                                | Stored has \"series/{id}\"                                       | | mu    | mangaupdates  | https://www.mangaupdates.com/series.html?id=`{id}`                                            | Stored has id                                                  | | nu    | novelupdates  | https://www.novelupdates.com/series/`{slug}`                                                  | Stored has slug                                                | | kt    | kitsu.io      | https://kitsu.io/api/edge/manga/`{id}` or https://kitsu.io/api/edge/manga?filter[slug]={slug} | If integer, use id version of the URL, otherwise use slug one  | | amz   | amazon        | N/A                                                                                           | Stored as full URL                                             | | ebj   | ebookjapan    | N/A                                                                                           | Stored as full URL                                             | | mal   | myanimelist   | https://myanimelist.net/manga/{id}                                                            | Store as id                                                    | | raw   | N/A           | N/A                                                                                           | Stored as full URL, untranslated stuff URL (original language) | | engtl | N/A           | N/A                                                                                           | Stored as full URL, official english licenced URL              |  # noqa: E501

    OpenAPI spec version: 5.0.21
    Contact: mangadexstaff@gmail.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class MangaAttributes(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        "title": "LocalizedString",
        "alt_titles": "list[LocalizedString]",
        "description": "LocalizedString",
        "is_locked": "bool",
        "links": "dict(str, str)",
        "original_language": "str",
        "last_volume": "str",
        "last_chapter": "str",
        "publication_demographic": "str",
        "status": "str",
        "year": "int",
        "content_rating": "str",
        "tags": "list[Tag]",
        "version": "int",
        "created_at": "str",
        "updated_at": "str",
    }

    attribute_map = {
        "title": "title",
        "alt_titles": "altTitles",
        "description": "description",
        "is_locked": "isLocked",
        "links": "links",
        "original_language": "originalLanguage",
        "last_volume": "lastVolume",
        "last_chapter": "lastChapter",
        "publication_demographic": "publicationDemographic",
        "status": "status",
        "year": "year",
        "content_rating": "contentRating",
        "tags": "tags",
        "version": "version",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
    }

    def __init__(
        self,
        title=None,
        alt_titles=None,
        description=None,
        is_locked=None,
        links=None,
        original_language=None,
        last_volume=None,
        last_chapter=None,
        publication_demographic=None,
        status=None,
        year=None,
        content_rating=None,
        tags=None,
        version=None,
        created_at=None,
        updated_at=None,
    ):  # noqa: E501
        """MangaAttributes - a model defined in Swagger"""  # noqa: E501
        self._title = None
        self._alt_titles = None
        self._description = None
        self._is_locked = None
        self._links = None
        self._original_language = None
        self._last_volume = None
        self._last_chapter = None
        self._publication_demographic = None
        self._status = None
        self._year = None
        self._content_rating = None
        self._tags = None
        self._version = None
        self._created_at = None
        self._updated_at = None
        self.discriminator = None
        if title is not None:
            self.title = title
        if alt_titles is not None:
            self.alt_titles = alt_titles
        if description is not None:
            self.description = description
        if is_locked is not None:
            self.is_locked = is_locked
        if links is not None:
            self.links = links
        if original_language is not None:
            self.original_language = original_language
        if last_volume is not None:
            self.last_volume = last_volume
        if last_chapter is not None:
            self.last_chapter = last_chapter
        if publication_demographic is not None:
            self.publication_demographic = publication_demographic
        if status is not None:
            self.status = status
        if year is not None:
            self.year = year
        if content_rating is not None:
            self.content_rating = content_rating
        if tags is not None:
            self.tags = tags
        if version is not None:
            self.version = version
        if created_at is not None:
            self.created_at = created_at
        if updated_at is not None:
            self.updated_at = updated_at

    @property
    def title(self):
        """Gets the title of this MangaAttributes.  # noqa: E501


        :return: The title of this MangaAttributes.  # noqa: E501
        :rtype: LocalizedString
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this MangaAttributes.


        :param title: The title of this MangaAttributes.  # noqa: E501
        :type: LocalizedString
        """

        self._title = title

    @property
    def alt_titles(self):
        """Gets the alt_titles of this MangaAttributes.  # noqa: E501


        :return: The alt_titles of this MangaAttributes.  # noqa: E501
        :rtype: list[LocalizedString]
        """
        return self._alt_titles

    @alt_titles.setter
    def alt_titles(self, alt_titles):
        """Sets the alt_titles of this MangaAttributes.


        :param alt_titles: The alt_titles of this MangaAttributes.  # noqa: E501
        :type: list[LocalizedString]
        """

        self._alt_titles = alt_titles

    @property
    def description(self):
        """Gets the description of this MangaAttributes.  # noqa: E501


        :return: The description of this MangaAttributes.  # noqa: E501
        :rtype: LocalizedString
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this MangaAttributes.


        :param description: The description of this MangaAttributes.  # noqa: E501
        :type: LocalizedString
        """

        self._description = description

    @property
    def is_locked(self):
        """Gets the is_locked of this MangaAttributes.  # noqa: E501


        :return: The is_locked of this MangaAttributes.  # noqa: E501
        :rtype: bool
        """
        return self._is_locked

    @is_locked.setter
    def is_locked(self, is_locked):
        """Sets the is_locked of this MangaAttributes.


        :param is_locked: The is_locked of this MangaAttributes.  # noqa: E501
        :type: bool
        """

        self._is_locked = is_locked

    @property
    def links(self):
        """Gets the links of this MangaAttributes.  # noqa: E501


        :return: The links of this MangaAttributes.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this MangaAttributes.


        :param links: The links of this MangaAttributes.  # noqa: E501
        :type: dict(str, str)
        """

        self._links = links

    @property
    def original_language(self):
        """Gets the original_language of this MangaAttributes.  # noqa: E501


        :return: The original_language of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._original_language

    @original_language.setter
    def original_language(self, original_language):
        """Sets the original_language of this MangaAttributes.


        :param original_language: The original_language of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._original_language = original_language

    @property
    def last_volume(self):
        """Gets the last_volume of this MangaAttributes.  # noqa: E501


        :return: The last_volume of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._last_volume

    @last_volume.setter
    def last_volume(self, last_volume):
        """Sets the last_volume of this MangaAttributes.


        :param last_volume: The last_volume of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._last_volume = last_volume

    @property
    def last_chapter(self):
        """Gets the last_chapter of this MangaAttributes.  # noqa: E501


        :return: The last_chapter of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._last_chapter

    @last_chapter.setter
    def last_chapter(self, last_chapter):
        """Sets the last_chapter of this MangaAttributes.


        :param last_chapter: The last_chapter of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._last_chapter = last_chapter

    @property
    def publication_demographic(self):
        """Gets the publication_demographic of this MangaAttributes.  # noqa: E501


        :return: The publication_demographic of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._publication_demographic

    @publication_demographic.setter
    def publication_demographic(self, publication_demographic):
        """Sets the publication_demographic of this MangaAttributes.


        :param publication_demographic: The publication_demographic of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._publication_demographic = publication_demographic

    @property
    def status(self):
        """Gets the status of this MangaAttributes.  # noqa: E501


        :return: The status of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this MangaAttributes.


        :param status: The status of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._status = status

    @property
    def year(self):
        """Gets the year of this MangaAttributes.  # noqa: E501

        Year of release  # noqa: E501

        :return: The year of this MangaAttributes.  # noqa: E501
        :rtype: int
        """
        return self._year

    @year.setter
    def year(self, year):
        """Sets the year of this MangaAttributes.

        Year of release  # noqa: E501

        :param year: The year of this MangaAttributes.  # noqa: E501
        :type: int
        """

        self._year = year

    @property
    def content_rating(self):
        """Gets the content_rating of this MangaAttributes.  # noqa: E501


        :return: The content_rating of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._content_rating

    @content_rating.setter
    def content_rating(self, content_rating):
        """Sets the content_rating of this MangaAttributes.


        :param content_rating: The content_rating of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._content_rating = content_rating

    @property
    def tags(self):
        """Gets the tags of this MangaAttributes.  # noqa: E501


        :return: The tags of this MangaAttributes.  # noqa: E501
        :rtype: list[Tag]
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """Sets the tags of this MangaAttributes.


        :param tags: The tags of this MangaAttributes.  # noqa: E501
        :type: list[Tag]
        """

        self._tags = tags

    @property
    def version(self):
        """Gets the version of this MangaAttributes.  # noqa: E501


        :return: The version of this MangaAttributes.  # noqa: E501
        :rtype: int
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this MangaAttributes.


        :param version: The version of this MangaAttributes.  # noqa: E501
        :type: int
        """

        self._version = version

    @property
    def created_at(self):
        """Gets the created_at of this MangaAttributes.  # noqa: E501


        :return: The created_at of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this MangaAttributes.


        :param created_at: The created_at of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._created_at = created_at

    @property
    def updated_at(self):
        """Gets the updated_at of this MangaAttributes.  # noqa: E501


        :return: The updated_at of this MangaAttributes.  # noqa: E501
        :rtype: str
        """
        return self._updated_at

    @updated_at.setter
    def updated_at(self, updated_at):
        """Sets the updated_at of this MangaAttributes.


        :param updated_at: The updated_at of this MangaAttributes.  # noqa: E501
        :type: str
        """

        self._updated_at = updated_at

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(MangaAttributes, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MangaAttributes):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
