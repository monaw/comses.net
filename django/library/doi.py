from .models import CodebaseRelease

from django.conf import settings

from datacite import DataCiteRESTClient, schema42
import logging, requests, json

logger = logging.getLogger(__name__)


def get_datacite_client():
    """
    Get a DataCite REST API client
    """
    return DataCiteRESTClient(
        username=settings.DATACITE_API_USERNAME,
        password=settings.DATACITE_API_PASSWORD,
        prefix=settings.DATACITE_PREFIX,
        test_mode=settings.DATACITE_TEST_MODE,
    )


def register_peer_reviewed_codebases():
    """
    Identify all codebases that have been peer reviewed, register them with DataCite DOI REST API and save their minted DOI.
    Allen suggests set codebase release doi to the draft doi, save it and if all successful, then update it to public
    """
    # codebase_releases = CodebaseRelease.objects.reviewed_without_doi().first()
    codebase_releases = [CodebaseRelease.objects.reviewed_without_doi().first()]
    # datacite_client = get_datacite_client()
    for release in codebase_releases:
        # logger.debug("Registering codebase release %s with DataCite", release)
        try:
            print("release doi = ", release.doi)
            # doi = datacite_client.public_doi(json_metadata, url=release.permanent_url)
            # logger.debug("minted public DOI: %s", doi)
            doi = __create_draft_doi(release)
            # release.doi = doi
            # release.save()
        except Exception as e:
            logger.error("DataCite error: %s", e)
            # FIXME: on failure, log to something and continue
            # https://github.com/comses/planning/issues/200
    return codebase_releases


def __create_draft_doi(release):
    print("entered __create_draft_doi")
    print("release : ", release)
    client = get_datacite_client()
    result = ""

    try:
        metadata = release.datacite.metadata
        print("metadata = ", metadata, "\n")
        assert schema42.validate(metadata), f"DataCite metadata failed validation"
        result = client.draft_doi(metadata)
        logger.debug("result is %s", result)
    except Exception as e:
        logger.error(e)
    return result


def mona_test():
    release = CodebaseRelease.objects.reviewed_without_doi().first()
    print("\nrelease = ", release, "\n")
    print("datacite metadata = ", release.datacite_metadata, "\n")
    # print("codemeta type = ", type(release.codemeta_json), "\n")
    # print("datacite type = ", type(release.datacite_json), "\n")
    client = get_datacite_client()

    payload = {"data": {"type": "dois"}}
    try:
        # works:
        # result = client.get_metadata("10.82853/rr29-8g69")

        """
        From https://datacite.readthedocs.io/en/latest/#usage
        doesn't work:
        """
        data = {
            "identifiers": [
                {
                    "identifierType": "DOI",
                    "identifier": "10.1234/foo.bar",
                }
            ],
            "creators": [
                {"name": "Smith, John"},
            ],
            "titles": [
                {
                    "title": "Minimal Test Case",
                }
            ],
            "publisher": "Invenio Software",
            "publicationYear": "2015",
            "types": {"resourceType": "Dataset", "resourceTypeGeneral": "Dataset"},
            "schemaVersion": "http://datacite.org/schema/kernel-4",
        }
        payload4 = {"data": {"type": "dois", "attributes": data}}
        # assert schema42.validate(payload4), f"data failed validation"
        # doc = schema42.tostring(data)
        result = client.draft_doi(payload4)

        """
        From https://support.datacite.org/reference/post_dois
        works!
        """
        url = "https://api.test.datacite.org/dois"
        headers = {
            "content-type": "application/json",
            "authorization": "Basic bGxnaC5obWJrd2I6TmdhUk5RM3pyeFN4dTly",
        }
        payload = {"data": {"type": "dois", "attributes": {"prefix": "10.82853"}}}
        payload2 = {
            "data": {
                "type": "dois",
                "attributes": {
                    "publisher": {
                        "name": "CoMSES Net https://www.comses.net/codebases"
                    },
                    "types": {
                        "resourceTypeGeneral": "Software",
                        "resourceType": "Model",
                    },
                    "prefix": "10.82853",
                    "descriptions": [
                        {
                            "description": "This model can be used to explore under which conditions agents behave as observed in field experiments on irrigation games. In irrigation games participants have different levels of access to the resource. This asymmetry causes that agents downstream reduce investment in the common infrastructure if they do not get a large enough share of the common pool. Participants balance efficiency and equity. When do agents evolve who do the same?",
                            "descriptionType": "Abstract",
                        }
                    ],
                    "identifiers": [
                        {
                            "identifier": "http://mona.comses.net/codebases/2274/releases/1.0.0/",
                            "identifierType": "DOI",
                        }
                    ],
                    "titles": [
                        {
                            "title": "Evolution of Cooperation in Asymmetric Commons Dilemmas"
                        }
                    ],
                    "version": "1.0.0",
                },
            }
        }
        print("payload 2 type = ", type(payload2))

        """
        works!
        """
        # attributes = json.loads(release.datacite_metadata.to_json())
        attributes = release.datacite_metadata.metadata
        # print("attributes 1 = ", attributes)
        print("attributes type = ", type(attributes))
        attributes.update({"prefix": "10.82853"})
        # print("attributes 2 = ", attributes)
        # payload3 = {"data": {"type": "dois", "attributes": json.dumps(attributes)}}
        # payload3 = {"data": {"type": "dois", "attributes": json.dumps(attributes)}}
        payload3 = {"data": {"type": "dois", "attributes": attributes}}
        print("payload3 type = ", type(payload3), "\n")

        # result = requests.post(url, json=payload3, headers=headers)
        # print("result = (", result, ") ", result.text, "\n")

        """
        doesn't work:
        assert schema42.validate(attributes), f"attributes failed validation!"
        doc = schema42.tostring(attributes)
        print("doc : (", type(doc), ") ", doc)
        result = client.draft_doi(doc)
        print("result = ", result, "\n")
        """

        """
        payload 2
        result = {
            "data": {
                "id": "10.82853/8arm-gv91",
                "type": "dois",
                "attributes": {
                    "doi": "10.82853/8arm-gv91",
                    "prefix": "10.82853",
                    "suffix": "8arm-gv91",
                    "identifiers": [],
                    "alternateIdentifiers": [],
                    "creators": [],
                    "titles": [
                        {
                            "title": "Evolution of Cooperation in Asymmetric Commons Dilemmas"
                        }
                    ],
                    "publisher": "CoMSES Net https://www.comses.net/codebases",
                    "container": {},
                    "publicationYear": null,
                    "subjects": [],
                    "contributors": [],
                    "dates": [],
                    "language": null,
                    "types": {
                        "schemaOrg": "SoftwareSourceCode",
                        "citeproc": "article",
                        "bibtex": "misc",
                        "ris": "COMP",
                        "resourceTypeGeneral": "Software",
                        "resourceType": "Model",
                    },
                    "relatedIdentifiers": [],
                    "relatedItems": [],
                    "sizes": [],
                    "formats": [],
                    "version": "1.0.0",
                    "rightsList": [],
                    "descriptions": [
                        {
                            "description": "This model can be used to explore under which conditions agents behave as observed in field experiments on irrigation games. In irrigation games participants have different levels of access to the resource. This asymmetry causes that agents downstream reduce investment in the common infrastructure if they do not get a large enough share of the common pool. Participants balance efficiency and equity. When do agents evolve who do the same?",
                            "descriptionType": "Abstract",
                        }
                    ],
                    "geoLocations": [],
                    "fundingReferences": [],
                    "xml": "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHJlc291cmNlIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhtbG5zPSJodHRwOi8vZGF0YWNpdGUub3JnL3NjaGVtYS9rZXJuZWwtNCIgeHNpOnNjaGVtYUxvY2F0aW9uPSJodHRwOi8vZGF0YWNpdGUub3JnL3NjaGVtYS9rZXJuZWwtNCBodHRwOi8vc2NoZW1hLmRhdGFjaXRlLm9yZy9tZXRhL2tlcm5lbC00L21ldGFkYXRhLnhzZCI+CiAgPGlkZW50aWZpZXIgaWRlbnRpZmllclR5cGU9IkRPSSI+MTAuODI4NTMvOEFSTS1HVjkxPC9pZGVudGlmaWVyPgogIDxjcmVhdG9ycy8+CiAgPHRpdGxlcz4KICAgIDx0aXRsZT5Fdm9sdXRpb24gb2YgQ29vcGVyYXRpb24gaW4gQXN5bW1ldHJpYyBDb21tb25zIERpbGVtbWFzPC90aXRsZT4KICA8L3RpdGxlcz4KICA8cHVibGlzaGVyPkNvTVNFUyBOZXQgaHR0cHM6Ly93d3cuY29tc2VzLm5ldC9jb2RlYmFzZXM8L3B1Ymxpc2hlcj4KICA8cHVibGljYXRpb25ZZWFyLz4KICA8cmVzb3VyY2VUeXBlIHJlc291cmNlVHlwZUdlbmVyYWw9IlNvZnR3YXJlIj5Nb2RlbDwvcmVzb3VyY2VUeXBlPgogIDxzaXplcy8+CiAgPGZvcm1hdHMvPgogIDx2ZXJzaW9uPjEuMC4wPC92ZXJzaW9uPgogIDxkZXNjcmlwdGlvbnM+CiAgICA8ZGVzY3JpcHRpb24gZGVzY3JpcHRpb25UeXBlPSJBYnN0cmFjdCI+VGhpcyBtb2RlbCBjYW4gYmUgdXNlZCB0byBleHBsb3JlIHVuZGVyIHdoaWNoIGNvbmRpdGlvbnMgYWdlbnRzIGJlaGF2ZSBhcyBvYnNlcnZlZCBpbiBmaWVsZCBleHBlcmltZW50cyBvbiBpcnJpZ2F0aW9uIGdhbWVzLiBJbiBpcnJpZ2F0aW9uIGdhbWVzIHBhcnRpY2lwYW50cyBoYXZlIGRpZmZlcmVudCBsZXZlbHMgb2YgYWNjZXNzIHRvIHRoZSByZXNvdXJjZS4gVGhpcyBhc3ltbWV0cnkgY2F1c2VzIHRoYXQgYWdlbnRzIGRvd25zdHJlYW0gcmVkdWNlIGludmVzdG1lbnQgaW4gdGhlIGNvbW1vbiBpbmZyYXN0cnVjdHVyZSBpZiB0aGV5IGRvIG5vdCBnZXQgYSBsYXJnZSBlbm91Z2ggc2hhcmUgb2YgdGhlIGNvbW1vbiBwb29sLiBQYXJ0aWNpcGFudHMgYmFsYW5jZSBlZmZpY2llbmN5IGFuZCBlcXVpdHkuIFdoZW4gZG8gYWdlbnRzIGV2b2x2ZSB3aG8gZG8gdGhlIHNhbWU/PC9kZXNjcmlwdGlvbj4KICA8L2Rlc2NyaXB0aW9ucz4KPC9yZXNvdXJjZT4K",
                    "url": null,
                    "contentUrl": null,
                    "metadataVersion": 0,
                    "schemaVersion": null,
                    "source": "api",
                    "isActive": false,
                    "state": "draft",
                    "reason": null,
                    "landingPage": null,
                    "viewCount": 0,
                    "viewsOverTime": [],
                    "downloadCount": 0,
                    "downloadsOverTime": [],
                    "referenceCount": 0,
                    "citationCount": 0,
                    "citationsOverTime": [],
                    "partCount": 0,
                    "partOfCount": 0,
                    "versionCount": 0,
                    "versionOfCount": 0,
                    "created": "2024-04-09T03:13:41.000Z",
                    "registered": null,
                    "published": "",
                    "updated": "2024-04-09T03:13:41.000Z",
                },
                "relationships": {
                    "client": {"data": {"id": "llgh.hmbkwb", "type": "clients"}},
                    "provider": {"data": {"id": "llgh", "type": "providers"}},
                    "media": {"data": {"id": "10.82853/8arm-gv91", "type": "media"}},
                    "references": {"data": []},
                    "citations": {"data": []},
                    "parts": {"data": []},
                    "partOf": {"data": []},
                    "versions": {"data": []},
                    "versionOf": {"data": []},
                },
            }
        }
        """

        """
        payload 3 response 201
        result = {
            "data": {
                "id": "10.82853/7ber-f026",
                "type": "dois",
                "attributes": {
                    "doi": "10.82853/7ber-f026",
                    "prefix": "10.82853",
                    "suffix": "7ber-f026",
                    "identifiers": [],
                    "alternateIdentifiers": [],
                    "creators": [],
                    "titles": [
                        {
                            "title": "Evolution of Cooperation in Asymmetric Commons Dilemmas"
                        }
                    ],
                    "publisher": "CoMSES Net https://www.comses.net/codebases",
                    "container": {},
                    "publicationYear": null,
                    "subjects": [],
                    "contributors": [],
                    "dates": [],
                    "language": null,
                    "types": {
                        "schemaOrg": "SoftwareSourceCode",
                        "citeproc": "article",
                        "bibtex": "misc",
                        "ris": "COMP",
                        "resourceTypeGeneral": "Software",
                        "resourceType": "Model",
                    },
                    "relatedIdentifiers": [],
                    "relatedItems": [],
                    "sizes": [],
                    "formats": [],
                    "version": "1.0.0",
                    "rightsList": [],
                    "descriptions": [
                        {
                            "description": "This model can be used to explore under which conditions agents behave as observed in field experiments on irrigation games. In irrigation games participants have different levels of access to the resource. This asymmetry causes that agents downstream reduce investment in the common infrastructure if they do not get a large enough share of the common pool. Participants balance efficiency and equity. When do agents evolve who do the same?",
                            "descriptionType": "Abstract",
                        }
                    ],
                    "geoLocations": [],
                    "fundingReferences": [],
                    "xml": null,
                    "url": null,
                    "contentUrl": null,
                    "metadataVersion": 0,
                    "schemaVersion": null,
                    "source": "api",
                    "isActive": false,
                    "state": "draft",
                    "reason": null,
                    "landingPage": null,
                    "viewCount": 0,
                    "viewsOverTime": [],
                    "downloadCount": 0,
                    "downloadsOverTime": [],
                    "referenceCount": 0,
                    "citationCount": 0,
                    "citationsOverTime": [],
                    "partCount": 0,
                    "partOfCount": 0,
                    "versionCount": 0,
                    "versionOfCount": 0,
                    "created": "2024-04-09T20:15:33.000Z",
                    "registered": null,
                    "published": "",
                    "updated": "2024-04-09T20:15:33.000Z",
                },
                "relationships": {
                    "client": {"data": {"id": "llgh.hmbkwb", "type": "clients"}},
                    "provider": {"data": {"id": "llgh", "type": "providers"}},
                    "media": {"data": {"id": "10.82853/7ber-f026", "type": "media"}},
                    "references": {"data": []},
                    "citations": {"data": []},
                    "parts": {"data": []},
                    "partOf": {"data": []},
                    "versions": {"data": []},
                    "versionOf": {"data": []},
                },
            }
        }
        """
    except Exception as e:
        print("error =", e)
    return


# works!
def mona_test_datacite_pkg():
    release = CodebaseRelease.objects.reviewed_without_doi().first()
    client = get_datacite_client()

    try:
        # works:
        # result = client.get_metadata("10.82853/rr29-8g69")

        """
        From https://datacite.readthedocs.io/en/latest/#usage
        """
        data = {
            "identifiers": [
                {
                    "identifierType": "DOI",
                    "identifier": "10.1234/foo.bar",
                }
            ],
            "creators": [
                {"name": "Smith, John"},
            ],
            "titles": [
                {
                    "title": "Minimal Test Case",
                }
            ],
            "publisher": "Invenio Software",
            "publicationYear": "2015",
            "types": {"resourceType": "Dataset", "resourceTypeGeneral": "Dataset"},
            "schemaVersion": "http://datacite.org/schema/kernel-4",
        }
        # payload = {"data": {"type": "dois", "attributes": data}}
        assert schema42.validate(data), f"data failed validation"
        doc = schema42.tostring(data)
        print("doc = ", doc, "\n")
        result = client.draft_doi(data)
        logger.debug("result is %s", result)
    except Exception as e:
        logger.error(e)
    return


# works
def mona_test_request():
    headers = {
        "content-type": "application/json",
        "authorization": "Basic bGxnaC5obWJrd2I6TmdhUk5RM3pyeFN4dTly",
    }
    release = CodebaseRelease.objects.reviewed_without_doi().first()
    url = "https://api.test.datacite.org/dois"

    try:
        attributes = release.datacite_metadata.metadata
        attributes.update({"prefix": "10.82853"})
        payload3 = {"data": {"type": "dois", "attributes": attributes}}
        result = requests.post(url, json=payload3, headers=headers)
        print("\nresult = (", result, ") ", result.text, "\n")
    except Exception as e:
        print("error =", e)
    return


def mona_test_release():
    release = CodebaseRelease.objects.reviewed_without_doi().first()
    client = get_datacite_client()

    try:
        # works:
        # result = client.get_metadata("10.82853/rr29-8g69")

        """
        From https://datacite.readthedocs.io/en/latest/#usage
        data = {
            "identifiers": [
                {
                    "identifierType": "DOI",
                    "identifier": "10.1234/foo.bar",
                }
            ],
            "creators": [
                {"name": "Smith, John"},
            ],
            "titles": [
                {
                    "title": "Minimal Test Case",
                }
            ],
            "publisher": "Invenio Software",
            "publicationYear": "2015",
            "types": {"resourceType": "Dataset", "resourceTypeGeneral": "Dataset"},
            "schemaVersion": "http://datacite.org/schema/kernel-4",
        }
        """
        data = release.datacite_metadata.metadata
        # assert schema42.validate(data), f"data failed validation"
        # doc = schema42.tostring(data)
        # print("doc = ", doc, "\n")
        result = client.draft_doi(data)
        logger.debug("result is %s", result)
    except Exception as e:
        logger.error(e)
    return
