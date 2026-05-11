from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

site_url = "https://etanabiotechid.sharepoint.com/sites/PTEBIIntranet"
username = "dito.wibowo@id.etanabiotech.com"
password = "Jurangmangu6"

ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
web = ctx.web
ctx.load(web)
ctx.execute_query()
print(f"Berhasil! Site title: {web.title}")