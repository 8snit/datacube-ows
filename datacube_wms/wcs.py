from __future__ import absolute_import, division, print_function

from flask import render_template

from datacube_wms.data import get_map, feature_info
from datacube_wms.ogc_utils import resp_headers

from datacube_wms.ogc_exceptions import WCS1Exception


try:
    from datacube_wms.wms_cfg_local import service_cfg
except:
    from datacube_wms.wms_cfg import service_cfg
from datacube_wms.wms_layers import get_layers


def handle_wcs(nocase_args):
    operation = nocase_args.get("request", "").upper()
    # WMS operation Map
    if not operation:
        raise WCS1Exception("No operation specified", locator="Request parameter")
    elif operation == "GETCAPABILITIES":
        return get_capabilities(nocase_args)
    else:
        raise WCS1Exception("Unrecognised operation: %s" % operation, locator="Request parameter")


def get_capabilities(args):
    # TODO: Handle updatesequence request parameter for cache consistency.
    # Note: Only WCS v1.0.0 is fully supported at this stage, so no version negotiation is necessary
    # Extract layer metadata from Datacube.
    platforms = get_layers(refresh=True)
    section = args.get("section")
    if section:
        section = section.lower()
    show_service = False
    show_capability = False
    show_content_metadata = False
    if section is None or section == "/":
        show_service = True
        show_capability = True
        show_content_metadata = True
    elif section == "/wcs_capabilities/service":
        show_service = True
    elif section == "/wcs_capabilities/capability":
        show_capability = True
    elif section == "/wcs_capabilities/contentmetadata":
        show_content_metadata = True
    else:
        raise WCS1Exception("Invalid section", WCS1Exception.INVALID_PARAMETER_VALUE, locator="Section parameter")

    return (
            render_template("wcs_capabilities.xml",
                            show_service=show_service,
                            show_capability=show_capability,
                            show_content_metadata=show_content_metadata,
                            service=service_cfg,
                            platforms=platforms),
            200,
            resp_headers({
                    "Content-Type": "application/xml",
                    "Cache-Control": "no-cache",
                    "Cache-Control": "max-age=0"
            })
    )

