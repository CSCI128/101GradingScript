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



    async def getCWIDFromEmail(self, usernames: list[str]) -> list[tuple[str, str]]:
        cwidMap = []

        for i in range(0, len(usernames), 14):
            query = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                    select=["employeeId", "userPrincipalName"],
                    filter=f"userPrincipalName in ['{'\',\''.join(usernames[i:i+14])}'] and accountEnabled eq true",
                )

            requestConfig = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(query_parameters=query)
            userCwids = await self.client.users.get(requestConfig)

            if userCwids is None:
                continue

            cwidMap.extend([(val.user_principal_name, val.employee_id) for val in userCwids.value])

        return cwidMap

    async def getEmailFromCWID(self, cwid: str) -> str:
        query = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                select=["userPrincipalName"],
                filter=f"employeeId eq '{cwid}' and accountEnabled eq true",
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

