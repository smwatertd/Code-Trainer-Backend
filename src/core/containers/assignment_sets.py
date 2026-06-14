from __future__ import annotations

from dependency_injector import containers, providers

from src.features.assignment_sets.services.assignment_set_service import AssignmentSetService
from src.features.assignment_sets.usecases import (
    AddAssignmentSetItemUseCase,
    CreateAssignmentSetUseCase,
    GetAssignmentSetUseCase,
    ListAccessibleAssignmentSetsUseCase,
    ListTeacherAssignmentSetsUseCase,
    RemoveAssignmentSetItemUseCase,
    UpdateAssignmentSetUseCase,
)


class AssignmentSetsContainer(containers.DeclarativeContainer):
    uow = providers.Dependency()
    group_service = providers.Dependency()

    assignment_set_service = providers.Factory(
        AssignmentSetService,
        uow=uow,
        group_service=group_service,
    )

    create_assignment_set_use_case = providers.Factory(
        CreateAssignmentSetUseCase,
        service=assignment_set_service,
    )
    list_teacher_assignment_sets_use_case = providers.Factory(
        ListTeacherAssignmentSetsUseCase,
        service=assignment_set_service,
    )
    list_accessible_assignment_sets_use_case = providers.Factory(
        ListAccessibleAssignmentSetsUseCase,
        service=assignment_set_service,
    )
    get_assignment_set_use_case = providers.Factory(
        GetAssignmentSetUseCase,
        service=assignment_set_service,
    )
    update_assignment_set_use_case = providers.Factory(
        UpdateAssignmentSetUseCase,
        service=assignment_set_service,
    )
    add_assignment_set_item_use_case = providers.Factory(
        AddAssignmentSetItemUseCase,
        service=assignment_set_service,
    )
    remove_assignment_set_item_use_case = providers.Factory(
        RemoveAssignmentSetItemUseCase,
        service=assignment_set_service,
    )
