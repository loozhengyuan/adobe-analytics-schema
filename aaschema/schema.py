import logging
import re
import enum

# Create logger object
logger = logging.getLogger(__name__)

# Custom field regex pattern
CUSTOM_FIELD_REGEX = re.compile(r"(?:post_)?(prop|evar|mvvar|hier)[0-9]+")

# List of columns that contains foreign key to a lookup table.
# https://docs.adobe.com/content/help/en/analytics/export/analytics-data-feed/data-feed-contents/datafeeds-reference.html
# NOTE: Although these columns are usually of signed integer type
# (or whatever Adobe Analytics may declare it as), it is safer
# to declare it as a string in your data warehouse in case you
# desire to normalise the data in future.
FOREIGN_KEY_COLUMNS = [
    "browser",              # browser.tsv (INFERRED: browser_type.tsv)
    "carrier",              # -- NOT KNOWN
    "color",                # color_depth.tsv
    "connection_type",      # connection_type.tsv
    "country",              # country.tsv
    "event_list",           # event.tsv
    "first_hit_ref_type",   # referrer_type.tsv
    "javascript",           # -- INFERRED: javascript_version.tsv
    "language",             # languages.tsv
    "os",                   # -- INFERRED: operating_systems.tsv
    "page_event",           # -- SEE: Adobe Analytics Docs
    "plugins",              # plugins.tsv
    "resolution",           # resolution.tsv
    "search_engine",        # search_engines.tsv
    "va_closer_id",         # -- SEE: Marketing Channel Manager
    "va_finder_id",         # -- SEE: Marketing Channel Manager
    "visit_ref_type",       # referrer_type.tsv
    "visit_search_engine",  # search_engines.tsv
]

# List of columns that deemed as deprecated by Adobe Analytics
# https://docs.adobe.com/content/help/en/analytics/export/analytics-data-feed/data-feed-contents/datafeeds-reference.html
DEPRECATED_COLUMNS = [
    # Non-post columns
    "mobileacquisitionclicks",
    "mobileactioninapptime",
    "mobileactiontotaltime",
    "mobileappperformanceaffectedusers",
    "mobileappperformanceappid.app-perf-app-name",
    "mobileappperformanceappid.app-perf-platform",
    "mobileappperformancecrashes",
    "mobileappperformancecrashid.app-perf-crash-name",
    "mobileappperformanceloads",
    "mobileappstoreavgrating",
    "mobileappstoredownloads",
    "mobileappstoreinapprevenue",
    "mobileappstoreinapproyalties",
    "mobileappstoreobjectid.app-store-user",
    "mobileappstoreobjectid.application-name",
    "mobileappstoreobjectid.application-version",
    "mobileappstoreobjectid.appstore-name",
    "mobileappstoreobjectid.category-name",
    "mobileappstoreobjectid.country-name",
    "mobileappstoreobjectid.device-manufacturer",
    "mobileappstoreobjectid.device-name",
    "mobileappstoreobjectid.in-app-name",
    "mobileappstoreobjectid.platform-name-version",
    "mobileappstoreobjectid.rank-category-type",
    "mobileappstoreobjectid.region-name",
    "mobileappstoreobjectid.review-comment",
    "mobileappstoreobjectid.review-title",
    "mobileappstoreoneoffrevenue",
    "mobileappstoreoneoffroyalties",
    "mobileappstorepurchases",
    "mobileappstorerank",
    "mobileappstorerankdivisor",
    "mobileappstorerating",
    "mobileappstoreratingdivisor",
    "mobileavgprevsessionlength",
    "mobilecrashes",
    "mobilecrashrate",
    "mobiledailyengagedusers",
    "mobiledeeplinkid.name",
    "mobileinstalls",
    "mobilelaunches",
    "mobileltvtotal",
    "mobilemessageclicks",
    "mobilemessageid.dest",
    "mobilemessageid.name",
    "mobilemessageid.type",
    "mobilemessageimpressions",
    "mobilemessagepushpayloadid.name",
    "mobilemessageviews",
    "mobilemonthlyengagedusers",
    "mobileplacedwelltime",
    "mobileplaceentry",
    "mobileplaceexit",
    "mobileprevsessionlength",
    "mobilerelaunchcampaigntrackingcode.name",
    "mobileupgrades",
    "socialaveragesentiment",
    "socialaveragesentiment (deprecated)",
    "socialfbstories",
    "socialfbstorytellers",
    "socialinteractioncount",
    "sociallikeadds",
    "sociallink",
    "sociallink (deprecated)",
    "socialmentions",
    "socialpageviews",
    "socialpostviews",
    "socialproperty",
    "socialproperty (deprecated)",
    "socialpubcomments",
    "socialpubposts",
    "socialpubrecommends",
    "socialpubsubscribers",
    "socialterm",
    "socialtermslist",
    "socialtermslist (deprecated)",
    "socialtotalsentiment",
    "sourceid",
    "videoauthorized",
    "videoaverageminuteaudience",
    "videochaptercomplete",
    "videochapterstart",
    "videochaptertime",
    "videopause",
    "videopausecount",
    "videopausetime",
    "videoplay",
    "videoprogress10",
    "videoprogress25",
    "videoprogress50",
    "videoprogress75",
    "videoprogress96",
    "videoqoebitrateaverage",
    "videoqoebitratechange",
    "videoqoebuffer",
    "videoqoedropbeforestart",
    "videoqoedroppedframes",
    "videoqoeerror",
    "videoresume",
    "videototaltime",
    "videouniquetimeplayed",
    # Post columns
    "post_mobileacquisitionclicks",
    "post_mobileactioninapptime",
    "post_mobileactiontotaltime",
    "post_mobileappperformanceaffectedusers",
    "post_mobileappperformanceappid.app-perf-app-name",
    "post_mobileappperformanceappid.app-perf-platform",
    "post_mobileappperformancecrashes",
    "post_mobileappperformancecrashid.app-perf-crash-name",
    "post_mobileappperformanceloads",
    "post_mobileappstoreavgrating",
    "post_mobileappstoredownloads",
    "post_mobileappstoreinapprevenue",
    "post_mobileappstoreinapproyalties",
    "post_mobileappstoreobjectid.app-store-user",
    "post_mobileappstoreobjectid.application-name",
    "post_mobileappstoreobjectid.application-version",
    "post_mobileappstoreobjectid.appstore-name",
    "post_mobileappstoreobjectid.category-name",
    "post_mobileappstoreobjectid.country-name",
    "post_mobileappstoreobjectid.device-manufacturer",
    "post_mobileappstoreobjectid.device-name",
    "post_mobileappstoreobjectid.in-app-name",
    "post_mobileappstoreobjectid.platform-name-version",
    "post_mobileappstoreobjectid.rank-category-type",
    "post_mobileappstoreobjectid.region-name",
    "post_mobileappstoreobjectid.review-comment",
    "post_mobileappstoreobjectid.review-title",
    "post_mobileappstoreoneoffrevenue",
    "post_mobileappstoreoneoffroyalties",
    "post_mobileappstorepurchases",
    "post_mobileappstorerank",
    "post_mobileappstorerankdivisor",
    "post_mobileappstorerating",
    "post_mobileappstoreratingdivisor",
    "post_mobileavgprevsessionlength",
    "post_mobilecrashes",
    "post_mobilecrashrate",
    "post_mobiledailyengagedusers",
    "post_mobiledeeplinkid.name",
    "post_mobileinstalls",
    "post_mobilelaunches",
    "post_mobileltvtotal",
    "post_mobilemessageclicks",
    "post_mobilemessageid.dest",
    "post_mobilemessageid.name",
    "post_mobilemessageid.type",
    "post_mobilemessageimpressions",
    "post_mobilemessagepushpayloadid.name",
    "post_mobilemessageviews",
    "post_mobilemonthlyengagedusers",
    "post_mobileplacedwelltime",
    "post_mobileplaceentry",
    "post_mobileplaceexit",
    "post_mobileprevsessionlength",
    "post_mobilerelaunchcampaigntrackingcode.name",
    "post_mobileupgrades",
    "post_socialaveragesentiment",
    "post_socialaveragesentiment (deprecated)",
    "post_socialfbstories",
    "post_socialfbstorytellers",
    "post_socialinteractioncount",
    "post_sociallikeadds",
    "post_sociallink",
    "post_sociallink (deprecated)",
    "post_socialmentions",
    "post_socialpageviews",
    "post_socialpostviews",
    "post_socialproperty",
    "post_socialproperty (deprecated)",
    "post_socialpubcomments",
    "post_socialpubposts",
    "post_socialpubrecommends",
    "post_socialpubsubscribers",
    "post_socialterm",
    "post_socialtermslist",
    "post_socialtermslist (deprecated)",
    "post_socialtotalsentiment",
    "post_sourceid",
    "post_videoauthorized",
    "post_videoaverageminuteaudience",
    "post_videochaptercomplete",
    "post_videochapterstart",
    "post_videochaptertime",
    "post_videopause",
    "post_videopausecount",
    "post_videopausetime",
    "post_videoplay",
    "post_videoprogress10",
    "post_videoprogress25",
    "post_videoprogress50",
    "post_videoprogress75",
    "post_videoprogress96",
    "post_videoqoebitrateaverage",
    "post_videoqoebitratechange",
    "post_videoqoebuffer",
    "post_videoqoedropbeforestart",
    "post_videoqoedroppedframes",
    "post_videoqoeerror",
    "post_videoresume",
    "post_videototaltime",
    "post_videouniquetimeplayed",
]

# Map of known fields and its corresponding data type
# NOTE: These key-value pairs of field data types are
# directly retrieved from Adobe Analytics' website.
# Consequently, some keys (e.g. 'evar1 - evar250') may
# not represent a single field but multiple ones.
KNOWN_FIELD_TYPES = {
    "accept_language": "char(20)",
    "aemassetid": "text",
    "aemassetsource": "varchar(255)",
    "aemclickedassetid": "varchar(255)",
    "browser": "int unsigned",
    "browser_height": "smallint unsigned",
    "browser_width": "smallint unsigned",
    "c_color": "char(20)",
    "campaign": "varchar(255)",
    "carrier": "varchar(100)",
    "channel": "varchar(100)",
    "click_action": "varchar(100)",
    "click_action_type": "tinyint unsigned",
    "click_context": "varchar(255)",
    "click_context_type": "tinyint unsigned",
    "click_sourceid": "int unsigned",
    "click_tag": "char(10)",
    "clickmaplink": "varchar(255)",
    "clickmaplinkbyregion": "varchar(255)",
    "clickmappage": "varchar(255)",
    "clickmapregion": "varchar(255)",
    "code_ver": "char(16)",
    "color": "smallint unsigned",
    "connection_type": "tinyint unsigned",
    "cookies": "char(1)",
    "country": "smallint unsigned",
    "ct_connect_type": "char(20)",
    "curr_factor": "tinyint",
    "curr_rate": "decimal(24,12)",
    "currency": "char(8)",
    "cust_hit_time_gmt": "int",
    "cust_visid": "varchar(255)",
    "daily_visitor": "tinyint unsigned",
    "date_time": "datetime",
    "domain": "varchar(100)",
    "duplicate_events": "varchar(255)",
    "duplicate_purchase": "tinyint unsigned",
    "duplicated_from": "varchar(40)",
    "ef_id": "varchar(255)",
    "evar1 - evar250": "varchar(255)",
    "event_list": "text",
    "exclude_hit": "tinyint unsigned",
    "first_hit_page_url": "varchar(255)",
    "first_hit_pagename": "varchar(100)",
    "first_hit_ref_domain": "varchar(100)",
    "first_hit_ref_type": "tinyint unsigned",
    "first_hit_referrer": "varchar(255)",
    "first_hit_time_gmt": "int",
    "geo_city": "char(32)",
    "geo_country": "char(4)",
    "geo_dma": "int unsigned",
    "geo_region": "char(32)",
    "geo_zip": "varchar(16)",
    "hier1 - hier5": "varchar(255)",
    "hit_source": "tinyint unsigned",
    "hit_time_gmt": "int",
    "hitid_high": "bigint unsigned",
    "hitid_low": "bigint unsigned",
    "homepage": "char(1)",
    "hourly_visitor": "tinyint unsigned",
    "ip": "char(20)",
    "ip2": "char(20)",
    "j_jscript": "char(5)",
    "java_enabled": "char(1)",
    "javascript": "tinyint unsigned",
    "language": "smallint unsigned",
    "last_hit_time_gmt": "int",
    "last_purchase_num": "int unsigned",
    "last_purchase_time_gmt": "int",
    "latlon1": "varchar(255)",
    "latlon23": "varchar(255)",
    "latlon45": "varchar(255)",
    "mc_audiences": "text",
    "mcvisid": "varchar(255)",
    "mobile_id": "int",
    "mobileaction": "varchar(100)",
    "mobileappid": "varchar(255)",
    "mobileappperformanceappid": "varchar(255)",
    "mobileappperformancecrashid": "varchar(255)",
    "mobileappstoreobjectid": "varchar(255)",
    "mobilebeaconmajor": "varchar(100)",
    "mobilebeaconminor": "varchar(100)",
    "mobilebeaconproximity": "varchar(255)",
    "mobilebeaconuuid": "varchar(100)",
    "mobilecampaigncontent": "varchar(255)",
    "mobilecampaignmedium": "varchar(255)",
    "mobilecampaignname": "varchar(255)",
    "mobilecampaignsource": "varchar(255)",
    "mobilecampaignterm": "varchar(255)",
    "mobiledayofweek": "varchar(255)",
    "mobiledayssincefirstuse": "varchar(255)",
    "mobiledayssincelastupgrade": "varchar(255)",
    "mobiledayssincelastuse": "varchar(255)",
    "mobiledeeplinkid": "varchar(255)",
    "mobiledevice": "varchar(255)",
    "mobilehourofday": "varchar(255)",
    "mobileinstalldate": "varchar(255)",
    "mobilelaunchessincelastupgrade": "varchar(255)",
    "mobilelaunchnumber": "varchar(255)",
    "mobileltv": "varchar(255)",
    "mobilemessagebuttonname": "varchar(100)",
    "mobilemessageid": "varchar(255)",
    "mobilemessageonline": "varchar(255)",
    "mobilemessagepushoptin": "varchar(255)",
    "mobilemessagepushpayloadid": "varchar(255)",
    "mobileosenvironment": "varchar(255)",
    "mobileosversion": "varchar(255)",
    "mobileplaceaccuracy": "varchar(255)",
    "mobileplacecategory": "varchar(255)",
    "mobileplaceid": "varchar(255)",
    "mobilerelaunchcampaigncontent": "varchar(255)",
    "mobilerelaunchcampaignmedium": "varchar(255)",
    "mobilerelaunchcampaignsource": "varchar(255)",
    "mobilerelaunchcampaignterm": "varchar(255)",
    "mobilerelaunchcampaigntrackingcode": "varchar(255)",
    "mobileresolution": "varchar(255)",
    "monthly_visitor": "tinyint unsigned",
    "mvvar1 - mvvar3": "text",
    "namespace": "varchar(50)",
    "new_visit": "tinyint unsigned",
    "os": "int unsigned",
    "p_plugins": "text",
    "page_event": "tinyint unsigned",
    "page_event_var1": "text",
    "page_event_var2": "varchar(100)",
    "page_event_var3": "text",
    "page_type": "char(20)",
    "page_url": "varchar(255)",
    "pagename": "varchar(100)",
    "paid_search": "tinyint unsigned",
    "partner_plugins": "varchar(255)",
    "persistent_cookie": "char(1)",
    "plugins": "varchar(180)",
    "pointofinterest": "varchar(255)",
    "pointofinterestdistance": "varchar(255)",
    "post_ columns": "See respective non-post column",
    "prev_page": "int unsigned",
    "product_list": "text",
    "product_merchandising": "text",
    "prop1 - prop75": "varchar(100)",
    "purchaseid": "char(20)",
    "quarterly_visitor": "tinyint unsigned",
    "ref_domain": "varchar(100)",
    "ref_type": "tinyint unsigned",
    "referrer": "varchar(255)",
    "resolution": "smallint unsigned",
    "s_kwcid": "varchar(255)",
    "s_resolution": "char(20)",
    "sampled_hit": "char(1)",
    "search_engine": "smallint unsigned",
    "search_page_num": "smallint unsigned",
    "secondary_hit": "tinyint unsigned",
    "service": "char(2)",
    "socialaccountandappids": "varchar(255)",
    "socialassettrackingcode": "varchar(255)",
    "socialauthor": "varchar(255)",
    "socialcontentprovider": "varchar(255)",
    "socialinteractiontype": "varchar(255)",
    "sociallanguage": "varchar(255)",
    "sociallatlong": "varchar(255)",
    "socialowneddefinitioninsighttype": "varchar(255)",
    "socialowneddefinitioninsightvalue": "varchar(255)",
    "socialowneddefinitionmetric": "varchar(255)",
    "socialowneddefinitionpropertyvspost": "varchar(255)",
    "socialownedpostids": "varchar(255)",
    "socialownedpropertyid": "varchar(255)",
    "socialownedpropertyname": "varchar(255)",
    "socialownedpropertypropertyvsapp": "varchar(255)",
    "state": "varchar(50)",
    "stats_server": "char(30)",
    "t_time_info": "varchar(100)",
    "tnt": "text",
    "tnt_action": "text",
    "tnt_post_vista": "text",
    "transactionid": "text",
    "truncated_hit": "char(1)",
    "ua_color": "char(20)",
    "ua_os": "char(80)",
    "ua_pixels": "char(20)",
    "user_agent": "text",
    "user_hash": "int unsigned",
    "user_server": "varchar(100)",
    "userid": "int unsigned",
    "username": "char(40)",
    "va_closer_detail": "varchar(255)",
    "va_closer_id": "tinyint unsigned",
    "va_finder_detail": "varchar(255)",
    "va_finder_id": "tinyint unsigned",
    "va_instance_event": "tinyint unsigned",
    "va_new_engagement": "tinyint unsigned",
    "video": "varchar(255)",
    "videoad": "varchar(255)",
    "videoadinpod": "varchar(255)",
    "videoadlength": "varchar(255)",
    "videoadload": "varchar(255)",
    "videoadname": "varchar(255)",
    "videoadplayername": "varchar(255)",
    "videoadpod": "varchar(255)",
    "videoadvertiser": "varchar(255)",
    "videoaudioalbum": "varchar(255)",
    "videoaudioartist": "varchar(255)",
    "videoaudioauthor": "varchar(255)",
    "videoaudiolabel": "varchar(255)",
    "videoaudiopublisher": "varchar(255)",
    "videoaudiostation": "varchar(255)",
    "videocampaign": "varchar(255)",
    "videochannel": "varchar(255)",
    "videochapter": "varchar(255)",
    "videocontenttype": "varchar(255)",
    "videodaypart": "varchar(255)",
    "videoepisode": "varchar(255)",
    "videofeedtype": "varchar(255)",
    "videogenre": "text",
    "videolength": "varchar(255)",
    "videomvpd": "varchar(255)",
    "videoname": "varchar(255)",
    "videonetwork": "varchar(255)",
    "videopath": "varchar(100)",
    "videoplayername": "varchar(255)",
    "videoqoebitrateaverageevar": "varchar(255)",
    "videoqoebitratechangecountevar": "varchar(255)",
    "videoqoebuffercountevar": "varchar(255)",
    "videoqoebuffertimeevar": "varchar(255)",
    "videoqoedroppedframecountevar": "varchar(255)",
    "videoqoeerrorcountevar": "varchar(255)",
    "videoqoeextneralerrors": "text",
    "videoqoeplayersdkerrors": "text",
    "videoqoetimetostartevar": "varchar(255)",
    "videoseason": "varchar(255)",
    "videosegment": "varchar(255)",
    "videoshow": "varchar(255)",
    "videoshowtype": "varchar(255)",
    "videostreamtype": "varchar(255)",
    "visid_high": "bigint unsigned",
    "visid_low": "bigint unsigned",
    "visid_new": "char(1)",
    "visid_timestamp": "int",
    "visid_type": "tinyint unsigned",
    "visit_keywords": "varchar(244)",
    "visit_num": "int unsigned",
    "visit_page_num": "int unsigned",
    "visit_ref_domain": "varchar(100)",
    "visit_ref_type": "tinyint unsigned",
    "visit_referrer": "varchar(255)",
    "visit_search_engine": "smallint unsigned",
    "visit_start_page_url": "varchar(255)",
    "visit_start_pagename": "varchar(100)",
    "visit_start_time_gmt": "int",
    "weekly_visitor": "tinyint unsigned",
    "yearly_visitor": "tinyint unsigned",
    "zip": "varchar(50)",
}


@enum.unique
class OutputFormat(enum.Enum):
    AVRO = 1
    BIGQUERY = 2


def map_field_type(field: str) -> str:
    """
    Returns the known data type of a field

    Args:
        field (str): The name of the field to be mapped
    """

    # Return null data type if field is deprecated
    if field in DEPRECATED_COLUMNS:
        logger.debug(f"Returning 'null' data type because field '{field}' is deprecated")
        return "null"

    # Return string data type if field is a foreign key column
    # NOTE: Even if values are not mapped, these columns should remain as string
    # so that values can be mapped to eventually
    if field in FOREIGN_KEY_COLUMNS:
        logger.debug(f"Returning 'string' data type because field '{field}' is a foreign key column")
        return "string"

    # Return string data type if field is a custom field
    if CUSTOM_FIELD_REGEX.match(field):
        logger.debug(f"Returning 'string' data type because field '{field}' matches a custom field")
        return "string"

    # Lookup data type
    lookup = field
    if field.startswith("post_"):
        lookup = field[5:]  # Omit post_ prefix if field starts with one
    type_ = KNOWN_FIELD_TYPES.get(lookup)
    if not type_:
        # NOTE: The following columns are known to be unrecognised:
        # adclassificationcreative
        # adload
        # mobilepushoptin
        # mobilepushpayloadid
        # post_adclassificationcreative
        # post_adload
        # post_keywords
        # post_mobilepushoptin
        # post_mobilepushpayloadid
        # post_pagename_no_url
        # post_survey
        logger.error(f"Field '{field}' could not be mapped; defaulting to 'null' data type")
        return "null"
    return type_


def map_bigquery_field_type(type_: str) -> str:
    """
    Returns BigQuery-compatible data type

    Args:
        string (str): Name of column to be mapped

    Reference:
        https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types
    """
    # TODO: BigQuery enumerated types

    # Define mapping
    mapping = {
        "char(20)": "STRING",
        "text": "STRING",
        "varchar(255)": "STRING",
        "int unsigned": "NUMERIC",
        "smallint unsigned": "NUMERIC",
        "varchar(100)": "STRING",
        "tinyint unsigned": "NUMERIC",
        "char(10)": "STRING",
        "char(16)": "STRING",
        "char(1)": "STRING",
        "tinyint": "NUMERIC",
        "decimal(24,12)": "NUMERIC",
        "char(8)": "STRING",
        "int": "NUMERIC",
        "datetime": "TIMESTAMP",
        "varchar(40)": "STRING",
        "char(32)": "STRING",
        "char(4)": "STRING",
        "varchar(16)": "STRING",
        "bigint unsigned": "NUMERIC",
        "char(5)": "STRING",
        "varchar(50)": "STRING",
        "varchar(180)": "STRING",
        # "See respective non-post column": "STRING",
        "char(2)": "STRING",
        "char(30)": "STRING",
        "char(80)": "STRING",
        "char(40)": "STRING",
        "varchar(244)": "STRING",
    }

    # Map data type
    mapped = mapping.get(type_, None)
    if not mapped:
        logger.warning(f"Type {type_} could not be mapped; defaulting to STRING data type")
        mapped = "STRING"
    return mapped


def map_avro_field_type(type_: str) -> str:
    """
    Returns AVRO-compatible data type

    Args:
        string (str): Name of column to be mapped

    Reference:
        https://avro.apache.org/docs/current/spec.html#schemas
    """

    # Define mapping
    mapping = {
        "char(20)": "string",
        "text": "string",
        "varchar(255)": "string",
        "int unsigned": "long",
        "smallint unsigned": "long",
        "varchar(100)": "string",
        "tinyint unsigned": "long",
        "char(10)": "string",
        "char(16)": "string",
        "char(1)": "string",
        "tinyint": "long",
        # "decimal(24,12)": "bytes",  # Uses logical type
        "char(8)": "string",
        "int": "long",
        # "datetime": "long",  # Uses logical type
        "varchar(40)": "string",
        "char(32)": "string",
        "char(4)": "string",
        "varchar(16)": "string",
        "bigint unsigned": "long",
        "char(5)": "string",
        "varchar(50)": "string",
        "varchar(180)": "string",
        # "See respective non-post column": "string",
        "char(2)": "string",
        "char(30)": "string",
        "char(80)": "string",
        "char(40)": "string",
        "varchar(244)": "string",
        # TODO: Mapping for already-compatible data types
        "string": "string",
        "null": "null",
    }

    # TODO: Check for already-compatible data types

    # Map data type
    mapped = mapping.get(type_, None)
    if not mapped:
        logger.warning(f"Type '{type_}' could not be mapped; defaulting to 'string' data type")
        mapped = "string"
    return mapped


def generate_schema(headers: str, style: OutputFormat) -> dict:
    """
    Returns a schema dictionary mapped to its known data type

    Args:
        headers (list): list of headers to be mapped
        style (OutputFormat): style of data type to be returned
    """

    # Check style
    # TODO: Consider the difference between var in enum vs isinstance(var, enum)
    if not isinstance(style, OutputFormat):
        logger.fatal(f"Output format is not a valid OutputFormat: {style}")
        return

    # Loop fields and map data type
    logger.info("Mapping column headers")
    if style == OutputFormat.AVRO:
        schema_map = {field: map_avro_field_type(map_field_type(field)) for field in headers}
        return schema_map
