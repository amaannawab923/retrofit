"""AGV and simulation configuration models."""

from pydantic import BaseModel, Field


class AGVConfig(BaseModel):
    """Configuration for AGV (Automated Guided Vehicle) fleet."""

    count: int = Field(..., description="Number of AGVs in the fleet", gt=0)
    speed: float = Field(..., description="Maximum speed in meters per second", gt=0)
    turn_delay: float = Field(
        ..., description="Delay when making a turn in seconds", ge=0
    )
    width: float = Field(..., description="Width of the AGV in meters", gt=0)
    length: float = Field(..., description="Length of the AGV in meters", gt=0)
    battery_capacity: float = Field(
        ..., description="Battery capacity in watt-hours", gt=0
    )


class SimulationParams(BaseModel):
    """Parameters for warehouse simulation."""

    agv_config: AGVConfig = Field(..., description="AGV fleet configuration")
    task_rate: float = Field(
        ...,
        description="Rate of task generation (tasks per minute)",
        gt=0,
    )
    pick_time: float = Field(
        ..., description="Time to pick up an item in seconds", gt=0
    )
    drop_time: float = Field(
        ..., description="Time to drop off an item in seconds", gt=0
    )
    simulation_duration: float = Field(
        ..., description="Total simulation duration in seconds", gt=0
    )
