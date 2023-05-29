terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.34.0"
    }
  }
}

provider "google" {
  project     = "calis-top50"
  region      = "ASIA-SOUTHEAST2"
}

# create a variable for client id
variable "client_id" {
  type = string
  default = "327782085729-2ufk2e1fmmr67far9h9kdqlqnp7d0ssr.apps.googleusercontent.com"
}


resource "google_storage_bucket" "default" {
  name                        = "calis-gcf-source" # Every bucket name must be globally unique
  location                    = "ASIA-SOUTHEAST2"
  uniform_bucket_level_access = true
}


data "archive_file" "default" {
  type        = "zip"
  output_path = "/tmp/calis-gcf-source.zip"
  excludes    = ["terraform", "terraform.*", ".terraform", ".terraform.*", "venv", "venv.*", ".git", ".git.*", "__pycache__", ".*", ".vscode", "cred"]
  source_dir  = ".."
}
resource "google_storage_bucket_object" "object" {
  name   = format("%s-%s.zip", "calis-gcf-source.zip", data.archive_file.default.output_md5)
  bucket = google_storage_bucket.default.name
  source = data.archive_file.default.output_path # Add path to the zipped function source code
}

resource "google_cloudfunctions2_function" "default" {
  name        = "whoami"
  location    = "asia-southeast2"
  description = "auth echo for calis"

  build_config {
    runtime     = "python310"
    entry_point = "whoami" # Set the entry point
    environment_variables = {
      GOOGLE_CLIENT_ID = var.client_id
    }
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

resource "google_cloudfunctions2_function" "docs" {
  name        = "docs"
  location    = "asia-southeast2"
  description = "docs"

  build_config {
    runtime     = "python310"
    entry_point = "docs" # Set the entry point
    environment_variables = {
      GOOGLE_CLIENT_ID = var.client_id
    }
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

resource "google_cloudfunctions2_function" "login" {
  name        = "login"
  location    = "asia-southeast2"
  description = "login and register for calis"

  build_config {
    runtime     = "python310"
    entry_point = "login" # Set the entry point
    environment_variables = {
      GOOGLE_CLIENT_ID = var.client_id
    }
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

resource "google_cloudfunctions2_function" "addChildren" {
  name        = "addChildren"
  location    = "asia-southeast2"
  description = "add children for account"

  build_config {
    runtime     = "python310"
    entry_point = "addChildren" # Set the entry point
    environment_variables = {
      GOOGLE_CLIENT_ID = var.client_id
    }
    source {
      storage_source {
        bucket = google_storage_bucket.default.name
        object = google_storage_bucket_object.object.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

output "whoami_url" {
  value = google_cloudfunctions2_function.default.service_config[0].uri
}
output "docs_url" {
  value = google_cloudfunctions2_function.docs.service_config[0].uri
}
output "login_url" {
  value = google_cloudfunctions2_function.login.service_config[0].uri
}
output "addChildren_url" {
  value = google_cloudfunctions2_function.addChildren.service_config[0].uri
}

