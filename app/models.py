from pydantic import BaseModel, ConfigDict, Field


class Recipe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    finding_group_ids: list[str] = Field(alias="findingGroupIds")
    impact: str
    likely_cause: str = Field(alias="likelyCause")
    action: str
    before_ttml: str = Field(alias="beforeTtml")
    proposed_ttml: str = Field(alias="proposedTtml")
    expected_outcome: str = Field(alias="expectedOutcome")
    guidance_ids: list[str] = Field(alias="guidanceIds")


class Analysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(alias="executiveSummary")
    delivery_status: str = Field(alias="deliveryStatus")
    priorities: list[str] = Field(max_length=3)
    recipes: list[Recipe]
    editorial_observations: list[str] = Field(alias="editorialObservations")
    limitations: list[str]
