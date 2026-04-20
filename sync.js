import axios from "axios";
import fs from "fs";
import path from "path";

const {
  TENANT_ID,
  CLIENT_ID,
  CLIENT_SECRET
} = process.env;

// 1. Get access token
async function getToken() {
  const res = await axios.post(
    `https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token`,
    new URLSearchParams({
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      scope: "https://graph.microsoft.com/.default",
      grant_type: "client_credentials"
    })
  );
  return res.data.access_token;
}

// 2. Get files from SharePoint
async function getFiles(token) {
  const res = await axios.get(
    `https://graph.microsoft.com/v1.0/sites/root/drives`,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  return res.data.value;
}

async function main() {
  const token = await getToken();
  const files = await getFiles(token);

  console.log(files);
}

main();