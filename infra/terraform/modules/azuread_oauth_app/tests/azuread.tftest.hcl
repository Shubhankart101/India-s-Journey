mock_provider "azuread" {
  mock_data "azuread_client_config" {
    defaults = {
      tenant_id = "00000000-0000-0000-0000-00000000aaaa"
      object_id = "00000000-0000-0000-0000-00000000bbbb"
    }
  }
}

mock_provider "time" {}

variables {
  hostnames = ["indias-journey.onrender.com", "data.example.in"]
}

run "registers_outlook_capable_app_with_callbacks" {
  command = plan

  assert {
    condition     = azuread_application.this.sign_in_audience == "AzureADandPersonalMicrosoftAccount"
    error_message = "Personal Outlook.com/Hotmail accounts must be allowed by default."
  }

  assert {
    condition = toset(azuread_application.this.web[0].redirect_uris) == toset([
      "https://indias-journey.onrender.com/accounts/microsoft/login/callback/",
      "https://data.example.in/accounts/microsoft/login/callback/",
    ])
    error_message = "Each hostname needs the allauth Microsoft callback."
  }

  assert {
    condition     = azuread_application.this.api[0].requested_access_token_version == 2
    error_message = "Personal accounts need v2 tokens."
  }

  assert {
    condition     = azuread_application.this.web[0].implicit_grant[0].access_token_issuance_enabled == false && azuread_application.this.web[0].implicit_grant[0].id_token_issuance_enabled == false
    error_message = "Implicit grant must stay disabled (authorization code + PKCE only)."
  }

  assert {
    condition     = one(one(azuread_application.this.required_resource_access).resource_access).id == "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
    error_message = "Only Microsoft Graph User.Read is requested."
  }

  assert {
    condition     = toset(azuread_application.this.owners) == toset(["00000000-0000-0000-0000-00000000bbbb"])
    error_message = "The caller owns the app when no owners are given."
  }

  assert {
    condition     = output.tenant == "common"
    error_message = "Work + personal accounts use the common tenant."
  }
}

run "localhost_redirect_is_opt_in" {
  command = plan

  variables {
    allow_localhost = true
  }

  assert {
    condition     = contains(azuread_application.this.web[0].redirect_uris, "http://localhost:8000/accounts/microsoft/login/callback/")
    error_message = "Localhost redirect must be added when requested."
  }
}

run "single_tenant_uses_tenant_id" {
  command = plan

  variables {
    sign_in_audience = "AzureADMyOrg"
  }

  assert {
    condition     = output.tenant == "00000000-0000-0000-0000-00000000aaaa"
    error_message = "Single-tenant apps must use the tenant ID."
  }
}

run "personal_only_uses_consumers" {
  command = plan

  variables {
    sign_in_audience = "PersonalMicrosoftAccount"
  }

  assert {
    condition     = output.tenant == "consumers"
    error_message = "Personal-only apps use the consumers tenant."
  }
}

run "requires_a_hostname" {
  command = plan

  variables {
    hostnames = []
  }

  expect_failures = [var.hostnames]
}
