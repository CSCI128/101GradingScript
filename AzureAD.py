from typing import List
from azure.identity import AzureCliCredential
from azure.core.credentials import TokenCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder


class AzureAD():

    SCOPES: List[str] = ["https://graph.microsoft.com/.default"]

    @staticmethod
    def _authenticate(tenantId: str) -> TokenCredential:
        # TODO - We will need to provide hints for this
        cred = AzureCliCredential(tenant_id=tenantId)

        return cred


    @staticmethod
    def _createGraphServiceClient(cred: TokenCredential, scopes = SCOPES) -> GraphServiceClient:
        client = GraphServiceClient(cred, scopes)

        return client
        


    def __init__(self, tenantId: str) -> None:
        self.cred = self._authenticate(tenantId)
        self.client = self._createGraphServiceClient(self.cred)



    async def getCWIDFromEmail(self, username: str) -> str:
        query = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                select=["employeeId"],
            )

        requestConfig = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(query_parameters=query)
        userCwid = await self.client.users.by_user_id(username).get(requestConfig)

        if userCwid is None or userCwid.employee_id is None:
            return ""

        return userCwid.employee_id

    async def getEmailFromCWID(self, cwid: str) -> str:
        query = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                select=["userPrincipalName"],
                # AAAAAA I THOUGHT I FINALLY ESCAPED ODATA
                # No idea why i have to do it like this???
                filter=f"employeeId eq '{cwid}'",
            )

        requestConfig = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(query_parameters=query)

        user = await self.client.users.get(requestConfig)

        if user is None:
            return ""

        if user.value is None or not len(user.value):
            return ""

        user = user.value[0]

        if user.user_principal_name is None:
          return ""

        return user.user_principal_name

