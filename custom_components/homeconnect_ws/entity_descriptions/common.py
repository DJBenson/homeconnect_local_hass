"""Description for BSH.Common Entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)
from homeassistant.components.number import NumberDeviceClass, NumberMode
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfTime

from .descriptions_definitions import (
    HCBinarySensorEntityDescription,
    HCButtonEntityDescription,
    HCNumberEntityDescription,
    HCSelectEntityDescription,
    HCSensorEntityDescription,
    HCSwitchEntityDescription,
    _EntityDescriptionsType,
)

if TYPE_CHECKING:
    from homeconnect_websocket import HomeAppliance


POWER_SWITCH_VALUE_MAPINGS = (
    ("On", "MainsOff"),
    ("Standby", "MainsOff"),
    ("On", "Off"),
    ("On", "Standby"),
    ("Standby", "Off"),
)


def generate_power_switch(appliance: HomeAppliance) -> HCSwitchEntityDescription | None:
    """Get Power switch description."""
    if entity := appliance.entities.get("BSH.Common.Setting.PowerState"):
        if entity.min and entity.max:
            # has min/max
            settable_states = set()
            for key, value in entity.enum.items():
                if int(key) >= entity.min and int(key) <= entity.max:
                    settable_states.add(value)
        else:
            settable_states = set(entity.enum.values())

        if len(settable_states) == 2:
            # only two power states
            for mapping in POWER_SWITCH_VALUE_MAPINGS:
                if settable_states == set(mapping):
                    return HCSwitchEntityDescription(
                        key="switch_power_state",
                        entity="BSH.Common.Setting.PowerState",
                        device_class=SwitchDeviceClass.SWITCH,
                        value_mapping=mapping,
                    )
    return None


def generate_power_select(appliance: HomeAppliance) -> HCSelectEntityDescription | None:
    """Get Power switch description."""
    if entity := appliance.entities.get("BSH.Common.Setting.PowerState"):
        if entity.min and entity.max:
            # has min/max
            settable_states = []
            for key, value in entity.enum.items():
                if int(key) >= entity.min and int(key) <= entity.max:
                    settable_states.append(str(value).lower())
        else:
            settable_states = [str(value).lower() for value in entity.enum.values()]

        return HCSelectEntityDescription(
            key="select_power_state",
            entity="BSH.Common.Setting.PowerState",
            options=settable_states,
            has_state_translation=True,
            # more then two power states
            entity_registry_enabled_default=len(settable_states) > 2,
        )
    return None


def generate_door_state(appliance: HomeAppliance) -> HCSensorEntityDescription | None:
    """Get Door sensor description."""
    entity = appliance.entities.get("BSH.Common.Status.DoorState")
    if entity and len(entity.enum) > 2:
        return HCSensorEntityDescription(
            key="sensor_door_state",
            entity="BSH.Common.Status.DoorState",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        )
    return None


COMMON_ENTITY_DESCRIPTIONS: _EntityDescriptionsType = {
    "abort_button": [
        HCButtonEntityDescription(
            key="button_abort_program",
            entity="BSH.Common.Command.AbortProgram",
        )
    ],
    "active_program": [
        HCSensorEntityDescription(
            key="sensor_active_program",
            entity="BSH.Common.Root.ActiveProgram",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        )
    ],
    "binary_sensor": [
        HCBinarySensorEntityDescription(
            key="binary_sensor_door_state",
            entity="BSH.Common.Status.DoorState",
            device_class=BinarySensorDeviceClass.DOOR,
            value_on={"Open", "Ajar"},
            value_off={"Closed", "Locked"},
        ),
        HCBinarySensorEntityDescription(
            key="binary_sensor_aqua_stop",
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity="BSH.Common.Event.AquaStopOccured",
            entity_registry_enabled_default=False,
            value_on={"Present"},
            value_off={"Off", "Confirmed"},
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        HCBinarySensorEntityDescription(
            key="binary_sensor_low_water_pressure",
            device_class=BinarySensorDeviceClass.PROBLEM,
            entity="BSH.Common.Event.LowWaterPressure",
            entity_registry_enabled_default=False,
            value_on={"Present"},
            value_off={"Off", "Confirmed"},
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        HCBinarySensorEntityDescription(
            key="binary_remote_start_allowed",
            entity="BSH.Common.Status.RemoteControlStartAllowed",
            entity_registry_enabled_default=False,
            entity_category=EntityCategory.CONFIG,
        ),
        HCBinarySensorEntityDescription(
            key="binary_sensor_program_aborted",
            entity="BSH.Common.Event.ProgramAborted",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=BinarySensorDeviceClass.PROBLEM,
            value_on={"Present", "Confirmed"},
            value_off={"Off"},
        ),
    ],
    "program": [
        HCSelectEntityDescription(
            key="select_program",
            entity="BSH.Common.Root.SelectedProgram",
            has_state_translation=True,
        )
    ],
    "select": [
        HCSelectEntityDescription(
            key="select_remote_control_level",
            entity="BSH.Common.Setting.RemoteControlLevel",
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
            has_state_translation=True,
        ),
        generate_power_select,
    ],
    "sensor": [
        HCSensorEntityDescription(
            key="sensor_remaining_program_time",
            entity="BSH.Common.Option.RemainingProgramTime",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
            extra_attributes=[
                {
                    "name": "Is Estimated",
                    "entity": "BSH.Common.Option.RemainingProgramTimeIsEstimated",
                }
            ],
        ),
        HCSensorEntityDescription(
            key="sensor_program_progress",
            entity="BSH.Common.Option.ProgramProgress",
            native_unit_of_measurement=PERCENTAGE,
        ),
        HCSensorEntityDescription(
            key="sensor_water_forecast",
            entity="BSH.Common.Option.WaterForecast",
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        HCSensorEntityDescription(
            key="sensor_energy_forecast",
            entity="BSH.Common.Option.EnergyForecast",
            native_unit_of_measurement=PERCENTAGE,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        HCSensorEntityDescription(
            key="sensor_operation_state",
            entity="BSH.Common.Status.OperationState",
            device_class=SensorDeviceClass.ENUM,
        ),
        HCSensorEntityDescription(
            key="sensor_start_in",
            entity="BSH.Common.Option.StartInRelative",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
        ),
        HCSensorEntityDescription(
            key="sensor_count_started",
            entity="BSH.Common.Status.Program.All.Count.Started",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            state_class=SensorStateClass.TOTAL_INCREASING,
            extra_attributes=[
                {
                    "name": "Last Start",
                    "entity": "BSH.Common.Status.ProgramSessionSummary.Latest",
                    "value_fn": lambda entity: entity.value["start"],
                },
                {
                    "name": "Last End",
                    "entity": "BSH.Common.Status.ProgramSessionSummary.Latest",
                    "value_fn": lambda entity: entity.value["end"],
                },
            ],
        ),
        HCSensorEntityDescription(
            key="sensor_count_completed",
            entity="BSH.Common.Status.Program.All.Count.Completed",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        HCSensorEntityDescription(
            key="sensor_end_trigger",
            entity="BSH.Common.Status.ProgramRunDetail.EndTrigger",
            device_class=SensorDeviceClass.ENUM,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            has_state_translation=True,
        ),
        HCSensorEntityDescription(
            key="sensor_power_state",
            entity="BSH.Common.Setting.PowerState",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSensorEntityDescription(
            key="sensor_flex_start",
            entity="BSH.Common.Status.FlexStart",
            device_class=SensorDeviceClass.ENUM,
            has_state_translation=True,
        ),
        HCSensorEntityDescription(
            key="sensor_estimated_remaining_program_time",
            entity="BSH.Common.Option.EstimatedTotalProgramTime",
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            suggested_unit_of_measurement=UnitOfTime.HOURS,
        ),
        generate_door_state,
    ],
    "start_button": [
        HCButtonEntityDescription(
            key="button_start_program",
            entity="BSH.Common.Root.ActiveProgram",
        )
    ],
    "start_in": [
        HCSelectEntityDescription(
            key="select_start_in",
            entity="BSH.Common.Option.StartInRelative",
        )
    ],
    "switch": [
        HCSwitchEntityDescription(
            key="switch_child_lock",
            entity="BSH.Common.Setting.ChildLock",
            device_class=SwitchDeviceClass.SWITCH,
        ),
        generate_power_switch,
    ],
    "number": [
        HCNumberEntityDescription(
            key="number_duration",
            entity="BSH.Common.Option.Duration",
            device_class=NumberDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            mode=NumberMode.AUTO,
        ),
    ],
}
