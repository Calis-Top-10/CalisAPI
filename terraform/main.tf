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
  name   = "calis-gcf-source.zip"
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

output "function_uri" {
  value = google_cloudfunctions2_function.default.service_config[0].uri
}