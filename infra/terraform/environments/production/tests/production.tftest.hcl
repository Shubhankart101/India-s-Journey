mock_provider "render" {}
mock_provider "github" {}
mock_provider "time" {}

mock_provider "azuread" {
  mock_data "azuread_client_config" {
    defaults = {
      tenant_id = "00000000-0000-0000-0000-00000000aaaa"
      object_id = "00000000-0000-0000-0000-00000000bbbb"
    }
  }
}

run "composes_render_microsoft_and_github" {
  command = plan

  variables {
    google_client_id     = "g-id"
    google_client_secret = "g-secret"
  }

  assert {
    condition     = output.google_redirect_uris == ["https://indias-journey.onrender.com/accounts/google/login/callback/"]
    error_message = "Google redirect URI must match allauth's callback on the Render host."
  }

  assert {
    condition     = length(module.microsoft_oauth) == 1
    error_message = "Microsoft app registration is created by default."
  }

  assert {
    condition     = module.github.pages_url == "https://shubhankart101.github.io/India-s-Journey/"
    error_message = "GitHub Pages backup URL must flow to the repository variables."
  }
}

run "custom_domain_becomes_the_public_url" {
  command = plan

  variables {
    custom_domains   = ["data.example.in"]
    enable_microsoft = false
  }

  assert {
    condition = output.google_redirect_uris == [
      "https://indias-journey.onrender.com/accounts/google/login/callback/",
      "https://data.example.in/accounts/google/login/callback/",
    ]
    error_message = "Every hostname needs a Google callback."
  }

  assert {
    condition     = length(module.microsoft_oauth) == 0 && output.microsoft_redirect_uris == []
    error_message = "Microsoft can be disabled."
  }
}
