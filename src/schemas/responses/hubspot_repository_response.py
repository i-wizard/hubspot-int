from src.schemas.responses.base_repository_response import RepositoryResponse


class CreateOrUpdateContactResponse(RepositoryResponse):
    ...


class CreateOrUpdateDealResponse(RepositoryResponse):
    ...

class CreateTicketResponse(RepositoryResponse):
    ...


class GetCrmObjectsResponse(RepositoryResponse):
    ...

class GetContactIDByEmailResponse(RepositoryResponse):
    ...