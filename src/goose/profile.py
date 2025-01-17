from typing import Mapping

from attrs import asdict, define, field

from goose.utils import ensure_list


@define
class ToolkitSpec:
    """Configuration for a Toolkit"""

    name: str
    requires: Mapping[str, str] = field(factory=dict)


@define
class ObserverSpec:
    """Configuration for an Observer (telemetry plugin)"""

    name: str


@define
class Profile:
    """The configuration for a run of goose"""

    provider: str
    processor: str
    accelerator: str
    moderator: str
    toolkits: list[ToolkitSpec] = field(factory=list, converter=ensure_list(ToolkitSpec))
    observers: list[ObserverSpec] = field(factory=list, converter=ensure_list(ObserverSpec))

    @toolkits.validator
    def check_toolkit_requirements(self, _: type["ToolkitSpec"], toolkits: list[ToolkitSpec]) -> None:
        # checks that the list of toolkits in the profile have their requirements
        installed_toolkits = set([toolkit.name for toolkit in toolkits])

        for toolkit in toolkits:
            toolkit_name = toolkit.name
            toolkit_requirements = toolkit.requires
            for _, req in toolkit_requirements.items():
                if req not in installed_toolkits:
                    msg = f"Toolkit {toolkit_name} requires {req} but it is not present"
                    raise ValueError(msg)

    def to_dict(self) -> dict[str, any]:
        return asdict(self)

    def profile_info(self) -> str:
        toolkit_names = [toolkit.name for toolkit in self.toolkits]
        observer_names = [observer.name for observer in self.observers]
        return (
            f"provider:{self.provider}, processor:{self.processor} "
            f"toolkits: {', '.join(toolkit_names)} "
            f"observers: {', '.join(observer_names)}"
        )


def default_profile(provider: str, processor: str, accelerator: str, **kwargs: dict[str, any]) -> Profile:
    """Get the default profile"""

    # TODO consider if the providers should have recommended models

    return Profile(
        provider=provider,
        processor=processor,
        accelerator=accelerator,
        moderator="synopsis",
        toolkits=[ToolkitSpec("synopsis")],
        observers=[ObserverSpec("langfuse")],
    )
