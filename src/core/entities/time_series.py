import re
from uuid import UUID
from typing import List, Dict
from pydantic import BaseModel, field_validator


class MeasurementDetails(BaseModel):
    uuid: UUID
    tags: List[str]
    fields: Dict[str, str | int | float]
    data_sources_info: List[List[str | int | float]]

    @field_validator('fields', mode='before')
    @classmethod
    def validate_fields(cls, v):
        if not isinstance(v, dict):
            raise ValueError("fields must be a dictionary")
        fields = v.copy()
        for k, value in v.items():
            if isinstance(value, str):
                if re.match(r"^[\d]+$", value):
                    fields[k] = int(value)
                elif re.match(r"^[\d]+[\.|\,][\d]+$", value):
                    fields[k] = float(value)
            elif not isinstance(value, (int, float)):
                raise ValueError(
                    f"Invalid value type for field '{k}': {type(value)}")
        return fields

    @field_validator('data_sources_info', mode='before')
    @classmethod
    def validate_data_sources(cls, v):
        if not isinstance(v, list):
            raise ValueError("data_sources_info must be a list")
        for entry in v:
            if not isinstance(entry, (tuple, list)):
                raise ValueError("data_sources_info must be a list of tuples or lists")
        return v
    

class Instance(BaseModel):
    ts_uuid: UUID
    tenant_uuid: UUID
    ts_backend: str
    measurements_list: List[str]
    measurements: List[MeasurementDetails]
