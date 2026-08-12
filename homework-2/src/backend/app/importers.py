import csv
import json
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError


SUPPORTED_IMPORT_FORMATS = {"csv", "json", "xml"}


class ImportParseError(ValueError):
    pass


def infer_format(filename: str) -> str:
    extension = Path(filename).suffix.lower().lstrip(".")
    if extension not in SUPPORTED_IMPORT_FORMATS:
        raise ImportParseError("Unsupported import format. Use CSV, JSON, or XML.")
    return extension


def parse_ticket_file(content: bytes, filename: str) -> list[dict[str, Any]]:
    file_format = infer_format(filename)
    text = decode_content(content)

    parsers: dict[str, Callable[[str], list[dict[str, Any]]]] = {
        "csv": parse_csv_tickets,
        "json": parse_json_tickets,
        "xml": parse_xml_tickets,
    }

    return parsers[file_format](text)


def decode_content(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ImportParseError("File must be valid UTF-8 text.") from exc


def parse_csv_tickets(text: str) -> list[dict[str, Any]]:
    try:
        reader = csv.DictReader(StringIO(text))
        if reader.fieldnames is None:
            raise ImportParseError("CSV file must include a header row.")

        records = [normalize_flat_record(row) for row in reader]
    except csv.Error as exc:
        raise ImportParseError(f"Malformed CSV file: {exc}") from exc

    if not records:
        raise ImportParseError("CSV file does not contain any ticket records.")

    return records


def parse_json_tickets(text: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ImportParseError(f"Malformed JSON file: {exc.msg}.") from exc

    if isinstance(data, dict) and "tickets" in data:
        data = data["tickets"]

    if not isinstance(data, list):
        raise ImportParseError("JSON import must be an array or an object with a tickets array.")

    if not data:
        raise ImportParseError("JSON file does not contain any ticket records.")

    records = []
    for item in data:
        if not isinstance(item, dict):
            raise ImportParseError("Each JSON ticket record must be an object.")
        records.append(normalize_nested_record(item))

    return records


def parse_xml_tickets(text: str) -> list[dict[str, Any]]:
    try:
        root = ElementTree.fromstring(text)
    except ParseError as exc:
        raise ImportParseError(f"Malformed XML file: {exc}.") from exc

    ticket_elements = list(root.findall(".//ticket"))
    if root.tag == "ticket":
        ticket_elements = [root]

    if not ticket_elements:
        raise ImportParseError("XML file does not contain any ticket records.")

    return [normalize_xml_ticket(element) for element in ticket_elements]


def normalize_xml_ticket(element: ElementTree.Element) -> dict[str, Any]:
    record: dict[str, Any] = {}

    for child in element:
        if child.tag == "metadata":
            record["metadata"] = {
                metadata_child.tag: clean_text(metadata_child.text)
                for metadata_child in child
            }
        elif child.tag == "tags":
            record["tags"] = [
                clean_text(tag.text)
                for tag in child.findall("tag")
                if clean_text(tag.text)
            ]
        else:
            record[child.tag] = clean_text(child.text)

    return normalize_nested_record(record)


def normalize_flat_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        key.strip(): clean_text(value)
        for key, value in record.items()
        if key is not None and clean_text(value) != ""
    }

    tags = normalized.pop("tags", None)
    if tags is not None:
        normalized["tags"] = split_list_field(tags)

    metadata = {}
    for source_key, target_key in (
        ("metadata_source", "source"),
        ("source", "source"),
        ("browser", "browser"),
        ("device_type", "device_type"),
    ):
        value = normalized.pop(source_key, None)
        if value not in (None, ""):
            metadata[target_key] = value

    if metadata:
        normalized["metadata"] = metadata

    return normalized


def normalize_nested_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        key: clean_text(value) if isinstance(value, str) else value
        for key, value in record.items()
        if value not in (None, "")
    }

    tags = normalized.get("tags")
    if isinstance(tags, str):
        normalized["tags"] = split_list_field(tags)

    metadata = normalized.get("metadata")
    if isinstance(metadata, dict):
        normalized["metadata"] = {
            key: clean_text(value) if isinstance(value, str) else value
            for key, value in metadata.items()
            if value not in (None, "")
        }

    return normalized


def split_list_field(value: str) -> list[str]:
    separator = ";" if ";" in value else ","
    return [item.strip() for item in value.split(separator) if item.strip()]


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
