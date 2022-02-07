/*
 * CodeBuild for our server_flask Docker image.
 */
module "codebuild" {
  source = "github.com/fogies/aws-infrastructure//terraform_common/codebuild"

  name = "uwscope_server_flask"
  source_archive = var.source_archive
}
