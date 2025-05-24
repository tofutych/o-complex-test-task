from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    model_config: ConfigDict = ConfigDict(  # pyright: ignore [reportIncompatibleVariableOverride]
        from_attributes=True,
        populate_by_name=True,
    )
