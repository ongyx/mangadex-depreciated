# coding: utf-8

# flake8: noqa

"""
    MangaDex API

    MangaDex is an ad-free manga reader offering high-quality images!  This document details our API as it is right now. It is in no way a promise to never change it, although we will endeavour to publicly notify any major change.  # Authentication  You can login with the `/auth/login` endpoint. On success, it will return a JWT that remains valid for 15 minutes along with a session token that allows refreshing without re-authenticating for 1 month.  # Rate limits  The API enforces rate-limits to protect our servers against malicious and/or mistaken use. The API keeps track of the requests on an IP-by-IP basis. Hence, if you're on a VPN, proxy or a shared network in general, the requests of other users on this network might affect you.  At first, a **global limit of 5 requests per second per IP address** is in effect.  > This limit is enforced across multiple load-balancers, and thus is not an exact value but rather a lower-bound that we guarantee. The exact value will be somewhere in the range `[5, 5*n]` (with `n` being the number of load-balancers currently active). The exact value within this range will depend on the current traffic patterns we are experiencing.  On top of this, **some endpoints are further restricted** as follows:  | Endpoint                           | Requests per time period    | Time period in minutes | |------------------------------------|--------------------------   |------------------------| | `POST   /account/create`           | 1                           | 60                     | | `GET    /account/activate/{code}`  | 30                          | 60                     | | `POST   /account/activate/resend`  | 5                           | 60                     | | `POST   /account/recover`          | 5                           | 60                     | | `POST   /account/recover/{code}`   | 5                           | 60                     | | `POST   /auth/login`               | 30                          | 60                     | | `POST   /auth/refresh`             | 30                          | 60                     | | `POST   /author`                   | 10                          | 60                     | | `PUT    /author`                   | 10                          | 1                      | | `DELETE /author/{id}`              | 10                          | 10                     | | `POST   /captcha/solve`            | 10                          | 10                     | | `POST   /chapter/{id}/read`        | 300                         | 10                     | | `PUT    /chapter/{id}`             | 10                          | 1                      | | `DELETE /chapter/{id}`             | 10                          | 1                      | | `POST   /manga`                    | 10                          | 60                     | | `PUT    /manga/{id}`               | 10                          | 60                     | | `DELETE /manga/{id}`               | 10                          | 10                     | | `POST   /cover`                    | 10                          | 1                      | | `PUT    /cover/{id}`               | 10                          | 1                      | | `DELETE /cover/{id}`               | 10                          | 10                     | | `POST   /group`                    | 10                          | 60                     | | `PUT    /group/{id}`               | 10                          | 1                      | | `DELETE /group/{id}`               | 10                          | 10                     | | `GET    /at-home/server/{id}`      | 60                          | 1                      |  Calling these endpoints will further provide details via the following headers about your remaining quotas:  | Header                    | Description                                                                 | |---------------------------|-----------------------------------------------------------------------------| | `X-RateLimit-Limit`       | Maximal number of requests this endpoint allows per its time period         | | `X-RateLimit-Remaining`   | Remaining number of requests within your quota for the current time period  | | `X-RateLimit-Retry-After` | Timestamp of the end of the current time period, as UNIX timestamp          |  # Captchas  Some endpoints may require captchas to proceed, in order to slow down automated malicious traffic. Legitimate users might also be affected, based on the frequency of write requests or due certain endpoints being particularly sensitive to malicious use, such as user signup.  Once an endpoint decides that a captcha needs to be solved, a 403 Forbidden response will be returned, with the error code `captcha_required_exception`. The sitekey needed for recaptcha to function is provided in both the `X-Captcha-Sitekey` header field, as well as in the error context, specified as `siteKey` parameter.  The captcha result of the client can either be passed into the repeated original request with the `X-Captcha-Result` header or alternatively to the `POST /captcha/solve` endpoint. The time a solved captcha is remembered varies across different endpoints and can also be influenced by individual client behavior.  Authentication is not required for the `POST /captcha/solve` endpoint, captchas are tracked both by client ip and logged in user id. If you are logged in, you want to send the session token along, so you validate the captcha for your client ip and user id at the same time, but it is not required.  # Reading a chapter using the API  ## Retrieving pages from the MangaDex@Home network  A valid [MangaDex@Home network](https://mangadex.network) page URL is in the following format: `{server-specific base url}/{temporary access token}/{quality mode}/{chapter hash}/{filename}`  There are currently 2 quality modes: - `data`: Original upload quality - `data-saver`: Compressed quality  Upon fetching a chapter from the API, you will find 4 fields necessary to compute MangaDex@Home page URLs:  | Field                        | Type     | Description                       | |------------------------------|----------|-----------------------------------| | `.data.id`                   | `string` | API Chapter ID                    | | `.data.attributes.hash`      | `string` | MangaDex@Home Chapter Hash        | | `.data.attributes.data`      | `array`  | data quality mode filenames       | | `.data.attributes.dataSaver` | `array`  | data-saver quality mode filenames |  Example ```json GET /chapter/{id}  {   ...,   \"data\": {     \"id\": \"e46e5118-80ce-4382-a506-f61a24865166\",     ...,     \"attributes\": {       ...,       \"hash\": \"e199c7d73af7a58e8a4d0263f03db660\",       \"data\": [         \"x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png\",         ...       ],       \"dataSaver\": [         \"x1-ab2b7c8f30c843aa3a53c29bc8c0e204fba4ab3e75985d761921eb6a52ff6159.jpg\",         ...       ]     }   } } ```  From this point you miss only the base URL to an assigned MangaDex@Home server for your client and chapter. This is retrieved via a `GET` request to `/at-home/server/{ chapter .data.id }`.  Example: ```json GET /at-home/server/e46e5118-80ce-4382-a506-f61a24865166  {   \"baseUrl\": \"https://abcdefg.hijklmn.mangadex.network:12345/some-token\" } ```  The full URL is the constructed as follows ``` { server .baseUrl }/{ quality mode }/{ chapter .data.attributes.hash }/{ chapter .data.attributes.{ quality mode }.[*] }  Examples  data quality: https://abcdefg.hijklmn.mangadex.network:12345/some-token/data/e199c7d73af7a58e8a4d0263f03db660/x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png        base url: https://abcdefg.hijklmn.mangadex.network:12345/some-token   quality mode: data   chapter hash: e199c7d73af7a58e8a4d0263f03db660       filename: x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png   data-saver quality: https://abcdefg.hijklmn.mangadex.network:12345/some-token/data-saver/e199c7d73af7a58e8a4d0263f03db660/x1-ab2b7c8f30c843aa3a53c29bc8c0e204fba4ab3e75985d761921eb6a52ff6159.jpg        base url: https://abcdefg.hijklmn.mangadex.network:12345/some-token   quality mode: data-saver   chapter hash: e199c7d73af7a58e8a4d0263f03db660       filename: x1-ab2b7c8f30c843aa3a53c29bc8c0e204fba4ab3e75985d761921eb6a52ff6159.jpg ```  If the server you have been assigned fails to serve images, you are allowed to call the `/at-home/server/{ chapter id }` endpoint again to get another server.  Whether successful or not, **please do report the result you encountered as detailed below**. This is so we can pull the faulty server out of the network.  ## Report  In order to keep track of the health of the servers in the network and to improve the quality of service and reliability, we ask that you call the MangaDex@Home report endpoint after each image you retrieve, whether successfully or not.  It is a `POST` request against `https://api.mangadex.network/report` and expects the following payload with our example above:  | Field                       | Type       | Description                                                                         | |-----------------------------|------------|-------------------------------------------------------------------------------------| | `url`                       | `string`   | The full URL of the image                                                           | | `success`                   | `boolean`  | Whether the image was successfully retrieved                                        | | `cached `                   | `boolean`  | `true` iff the server returned an `X-Cache` header with a value starting with `HIT` | | `bytes`                     | `number`   | The size in bytes of the retrieved image                                            | | `duration`                  | `number`   | The time in miliseconds that the complete retrieval (not TTFB) of this image took   |  Examples herafter.  **Success:** ```json POST https://api.mangadex.network/report Content-Type: application/json  {   \"url\": \"https://abcdefg.hijklmn.mangadex.network:12345/some-token/data/e199c7d73af7a58e8a4d0263f03db660/x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png\",   \"success\": true,   \"bytes\": 727040,   \"duration\": 235,   \"cached\": true } ```  **Failure:** ```json POST https://api.mangadex.network/report Content-Type: application/json  {  \"url\": \"https://abcdefg.hijklmn.mangadex.network:12345/some-token/data/e199c7d73af7a58e8a4d0263f03db660/x1-b765e86d5ecbc932cf3f517a8604f6ac6d8a7f379b0277a117dc7c09c53d041e.png\",  \"success\": false,  \"bytes\": 25,  \"duration\": 235,  \"cached\": false } ```  While not strictly necessary, this helps us monitor the network's healthiness, and we appreciate your cooperation towards this goal. If no one reports successes and failures, we have no way to know that a given server is slow/broken, which eventually results in broken image retrieval for everyone.  # Retrieving Covers from the API  ## Construct Cover URLs  ### Source (original/best quality)  `https://uploads.mangadex.org/covers/{ manga.id }/{ cover.filename }`<br/> The extension can be png, jpeg or gif.  Example: `https://uploads.mangadex.org/covers/8f3e1818-a015-491d-bd81-3addc4d7d56a/4113e972-d228-4172-a885-cb30baffff97.jpg`  ### <=512px wide thumbnail  `https://uploads.mangadex.org/covers/{ manga.id }/{ cover.filename }.512.jpg`<br/> The extension is always jpg.  Example: `https://uploads.mangadex.org/covers/8f3e1818-a015-491d-bd81-3addc4d7d56a/4113e972-d228-4172-a885-cb30baffff97.jpg.512.jpg`  ### <=256px wide thumbnail  `https://uploads.mangadex.org/covers/{ manga.id }/{ cover.filename }.256.jpg`<br/> The extension is always jpg.  Example: `https://uploads.mangadex.org/covers/8f3e1818-a015-491d-bd81-3addc4d7d56a/4113e972-d228-4172-a885-cb30baffff97.jpg.256.jpg`  ## ℹ️ Where to find Cover filename ?  Look at the [Get cover operation](#operation/get-cover) endpoint to get Cover information. Also, if you get a Manga resource, you'll have, if available a `covert_art` relationship which is the main cover id.  # Static data  ## Manga publication demographic  | Value            | Description               | |------------------|---------------------------| | shounen          | Manga is a Shounen        | | shoujo           | Manga is a Shoujo         | | josei            | Manga is a Josei          | | seinen           | Manga is a Seinen         |  ## Manga status  | Value            | Description               | |------------------|---------------------------| | ongoing          | Manga is still going on   | | completed        | Manga is completed        | | hiatus           | Manga is paused           | | cancelled        | Manga has been cancelled  |  ## Manga reading status  | Value            | |------------------| | reading          | | on_hold          | | plan\\_to\\_read   | | dropped          | | re\\_reading      | | completed        |  ## Manga content rating  | Value            | Description               | |------------------|---------------------------| | safe             | Safe content              | | suggestive       | Suggestive content        | | erotica          | Erotica content           | | pornographic     | Pornographic content      |  ## CustomList visibility  | Value            | Description               | |------------------|---------------------------| | public           | CustomList is public      | | private          | CustomList is private     |  ## Relationship types  | Value            | Description                    | |------------------|--------------------------------| | manga            | Manga resource                 | | chapter          | Chapter resource               | | cover_art        | A Cover Art for a manga `*`    | | author           | Author resource                | | artist           | Author resource (drawers only) | | scanlation_group | ScanlationGroup resource       | | tag              | Tag resource                   | | user             | User resource                  | | custom_list      | CustomList resource            |  `*` Note, that on manga resources you get only one cover_art resource relation marking the primary cover if there are more than one. By default this will be the latest volume's cover art. If you like to see all the covers for a given manga, use the cover search endpoint for your mangaId and select the one you wish to display.  ## Manga links data  In Manga attributes you have the `links` field that is a JSON object with some strange keys, here is how to decode this object:  | Key   | Related site  | URL                                                                                           | URL details                                                    | |-------|---------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------| | al    | anilist       | https://anilist.co/manga/`{id}`                                                               | Stored as id                                                   | | ap    | animeplanet   | https://www.anime-planet.com/manga/`{slug}`                                                   | Stored as slug                                                 | | bw    | bookwalker.jp | https://bookwalker.jp/`{slug}`                                                                | Stored has \"series/{id}\"                                       | | mu    | mangaupdates  | https://www.mangaupdates.com/series.html?id=`{id}`                                            | Stored has id                                                  | | nu    | novelupdates  | https://www.novelupdates.com/series/`{slug}`                                                  | Stored has slug                                                | | kt    | kitsu.io      | https://kitsu.io/api/edge/manga/`{id}` or https://kitsu.io/api/edge/manga?filter[slug]={slug} | If integer, use id version of the URL, otherwise use slug one  | | amz   | amazon        | N/A                                                                                           | Stored as full URL                                             | | ebj   | ebookjapan    | N/A                                                                                           | Stored as full URL                                             | | mal   | myanimelist   | https://myanimelist.net/manga/{id}                                                            | Store as id                                                    | | raw   | N/A           | N/A                                                                                           | Stored as full URL, untranslated stuff URL (original language) | | engtl | N/A           | N/A                                                                                           | Stored as full URL, official english licenced URL              |  # noqa: E501

    OpenAPI spec version: 5.0.21
    Contact: mangadexstaff@gmail.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

# import apis into sdk package
from mangadex_openapi.api.account_api import AccountApi
from mangadex_openapi.api.at_home_api import AtHomeApi
from mangadex_openapi.api.auth_api import AuthApi
from mangadex_openapi.api.author_api import AuthorApi
from mangadex_openapi.api.captcha_api import CaptchaApi
from mangadex_openapi.api.chapter_api import ChapterApi
from mangadex_openapi.api.cover_api import CoverApi
from mangadex_openapi.api.custom_list_api import CustomListApi
from mangadex_openapi.api.feed_api import FeedApi
from mangadex_openapi.api.infrastructure_api import InfrastructureApi
from mangadex_openapi.api.legacy_api import LegacyApi
from mangadex_openapi.api.manga_api import MangaApi
from mangadex_openapi.api.scanlation_group_api import ScanlationGroupApi
from mangadex_openapi.api.search_api import SearchApi
from mangadex_openapi.api.upload_api import UploadApi
from mangadex_openapi.api.user_api import UserApi

# import ApiClient
from mangadex_openapi.api_client import ApiClient
from mangadex_openapi.configuration import Configuration

# import models into sdk package
from mangadex_openapi.models.account_activate_response import AccountActivateResponse
from mangadex_openapi.models.author import Author
from mangadex_openapi.models.author_attributes import AuthorAttributes
from mangadex_openapi.models.author_create import AuthorCreate
from mangadex_openapi.models.author_edit import AuthorEdit
from mangadex_openapi.models.author_list import AuthorList
from mangadex_openapi.models.author_response import AuthorResponse
from mangadex_openapi.models.body import Body
from mangadex_openapi.models.body1 import Body1
from mangadex_openapi.models.chapter import Chapter
from mangadex_openapi.models.chapter_attributes import ChapterAttributes
from mangadex_openapi.models.chapter_edit import ChapterEdit
from mangadex_openapi.models.chapter_list import ChapterList
from mangadex_openapi.models.chapter_request import ChapterRequest
from mangadex_openapi.models.chapter_response import ChapterResponse
from mangadex_openapi.models.check_response import CheckResponse
from mangadex_openapi.models.cover import Cover
from mangadex_openapi.models.cover_attributes import CoverAttributes
from mangadex_openapi.models.cover_edit import CoverEdit
from mangadex_openapi.models.cover_list import CoverList
from mangadex_openapi.models.cover_response import CoverResponse
from mangadex_openapi.models.create_account import CreateAccount
from mangadex_openapi.models.create_scanlation_group import CreateScanlationGroup
from mangadex_openapi.models.custom_list import CustomList
from mangadex_openapi.models.custom_list_attributes import CustomListAttributes
from mangadex_openapi.models.custom_list_create import CustomListCreate
from mangadex_openapi.models.custom_list_edit import CustomListEdit
from mangadex_openapi.models.custom_list_list import CustomListList
from mangadex_openapi.models.custom_list_response import CustomListResponse
from mangadex_openapi.models.error import Error
from mangadex_openapi.models.error_response import ErrorResponse
from mangadex_openapi.models.inline_response200 import InlineResponse200
from mangadex_openapi.models.inline_response2001 import InlineResponse2001
from mangadex_openapi.models.inline_response2002 import InlineResponse2002
from mangadex_openapi.models.inline_response2003 import InlineResponse2003
from mangadex_openapi.models.inline_response2004 import InlineResponse2004
from mangadex_openapi.models.inline_response2005 import InlineResponse2005
from mangadex_openapi.models.inline_response200_chapters import (
    InlineResponse200Chapters,
)
from mangadex_openapi.models.inline_response200_volumes import InlineResponse200Volumes
from mangadex_openapi.models.localized_string import LocalizedString
from mangadex_openapi.models.login import Login
from mangadex_openapi.models.login_response import LoginResponse
from mangadex_openapi.models.login_response_token import LoginResponseToken
from mangadex_openapi.models.logout_response import LogoutResponse
from mangadex_openapi.models.manga import Manga
from mangadex_openapi.models.manga_attributes import MangaAttributes
from mangadex_openapi.models.manga_create import MangaCreate
from mangadex_openapi.models.manga_edit import MangaEdit
from mangadex_openapi.models.manga_list import MangaList
from mangadex_openapi.models.manga_request import MangaRequest
from mangadex_openapi.models.manga_response import MangaResponse
from mangadex_openapi.models.mapping_id import MappingId
from mangadex_openapi.models.mapping_id_attributes import MappingIdAttributes
from mangadex_openapi.models.mapping_id_body import MappingIdBody
from mangadex_openapi.models.mapping_id_response import MappingIdResponse
from mangadex_openapi.models.order import Order
from mangadex_openapi.models.order1 import Order1
from mangadex_openapi.models.order2 import Order2
from mangadex_openapi.models.order3 import Order3
from mangadex_openapi.models.order4 import Order4
from mangadex_openapi.models.order5 import Order5
from mangadex_openapi.models.order6 import Order6
from mangadex_openapi.models.recover_complete_body import RecoverCompleteBody
from mangadex_openapi.models.refresh_response import RefreshResponse
from mangadex_openapi.models.refresh_token import RefreshToken
from mangadex_openapi.models.relationship import Relationship
from mangadex_openapi.models.response import Response
from mangadex_openapi.models.scanlation_group import ScanlationGroup
from mangadex_openapi.models.scanlation_group_attributes import (
    ScanlationGroupAttributes,
)
from mangadex_openapi.models.scanlation_group_edit import ScanlationGroupEdit
from mangadex_openapi.models.scanlation_group_list import ScanlationGroupList
from mangadex_openapi.models.scanlation_group_response import ScanlationGroupResponse
from mangadex_openapi.models.scanlation_group_response_relationships import (
    ScanlationGroupResponseRelationships,
)
from mangadex_openapi.models.send_account_activation_code import (
    SendAccountActivationCode,
)
from mangadex_openapi.models.tag import Tag
from mangadex_openapi.models.tag_attributes import TagAttributes
from mangadex_openapi.models.tag_response import TagResponse
from mangadex_openapi.models.update_manga_status import UpdateMangaStatus
from mangadex_openapi.models.user import User
from mangadex_openapi.models.user_attributes import UserAttributes
from mangadex_openapi.models.user_list import UserList
from mangadex_openapi.models.user_response import UserResponse

from mangadex_openapi.wrapper.core import QuickClient

__version__ = "0.4.1"
