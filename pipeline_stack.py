from aws_cdk import (core, aws_codebuild as codebuild,

                     aws_codepipeline as codepipeline,
                     aws_codepipeline_actions as codepipeline_actions,
                     aws_secretsmanager as secret,
                     aws_lambda as lambda_, aws_s3 as s3)

class PipelineStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *,
                 lambda_code: lambda_.CfnParametersCode = None, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


        secret_arn='arn:aws:secretsmanager:us-east-1:417302553802:secret:indrahrpkey-Eg83NU'
        sec=secret.Secret.from_secret_arn(self,'secret',secret_arn)
        sv=sec.secret_value_from_json("github")


        cdk_build = codebuild.PipelineProject(self, "CdkBuild",
                                              build_spec=codebuild.BuildSpec.from_object(dict(
                                                  version="0.2",
                                                  phases=dict(
                                                      install=dict(
                                                          runtime="versions=nodejs:  8",

                                                          commands=["npm install -g aws-cdk",
                                                                    "pip install aws-cdk.aws-codepipeline",
                                                                    "pip install aws-cdk.core",
                                                                    "pip install aws-cdk.aws-codepipeline_actions",
                                                                    "pip install aws-cdk.aws_secretsmanager",
                                                                    "pip install aws-cdk.aws_lambda",
                                                                    "pip install aws-cdk.aws_codebuild",
                                                                    "pip install aws-cdk.aws_codedeploy",
                                                                    "pip install aws_cdk.app_delivery"
                                                            ]

                                                                    ),

                                                      build=dict(commands=[
                                                          "npm install -g aws-cdk",
                                                          "cdk synth PipelineDeployingLambdaStack -o dist"])),
                                                  artifacts={
                                                      "base-directory": "dist",
                                                      "files": [
                                                          "LambdaStack.template.json"]},
                                                  environment=dict(buildImage=
                                                                   codebuild.LinuxBuildImage.STANDARD_2_0))))

        lambda_build = codebuild.PipelineProject(self, 'LambdaBuild',
                                                 build_spec=codebuild.BuildSpec.from_object(dict(
                                                     version="0.2",
                                                     phases=dict(
                                                         install=dict(
                                                             commands=[
                                                                 "echo 'install' ",
                                                                 ]),
                                                         build=dict(
                                                             commands="cd lambda")),
                                                     artifacts={
                                                         "base-directory": "lambda",
                                                         "files": [
                                                             "index.js",
                                                             ]},
                                                     environment=dict(buildImage=
                                                                      codebuild.LinuxBuildImage.STANDARD_2_0))))

        source_output = codepipeline.Artifact()
        cdk_build_output = codepipeline.Artifact("CdkBuildOutput")
        lambda_build_output = codepipeline.Artifact("LambdaBuildOutput")

        lambda_location = lambda_build_output.s3_location

        source = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub",
            output=source_output,
            repo='testrepo',
            oauth_token=sv,
            owner='indrasema4'
        )

        codepipeline.Pipeline(self, "Pipeline",
                              stages=[
                                  codepipeline.StageProps(stage_name="Source",
                                                          actions=[
                                                             source]),
                                  codepipeline.StageProps(stage_name="Build",
                                                          actions=[
                                                              codepipeline_actions.CodeBuildAction(
                                                                  action_name="Lambda_Build",
                                                                  project=lambda_build,
                                                                  input=source_output,
                                                                  outputs=[lambda_build_output]),
                                                              codepipeline_actions.CodeBuildAction(
                                                                  action_name="CDK_Build",
                                                                  project=cdk_build,
                                                                  input=source_output,
                                                                  outputs=[cdk_build_output])]),
                                  codepipeline.StageProps(stage_name="Deploy",
                                                          actions=[
                                                              codepipeline_actions.CloudFormationCreateUpdateStackAction(
                                                                  action_name="Lambda_CFN_Deploy",
                                                                  template_path=cdk_build_output.at_path(
                                                                      "LambdaStack.template.json"),
                                                                  stack_name="LambdaDeploymentStack",
                                                                  admin_permissions=True,
                                                                  parameter_overrides=dict(
                                                                      lambda_code.assign(
                                                                          bucket_name=lambda_location.bucket_name,
                                                                          object_key=lambda_location.object_key,
                                                                          object_version=lambda_location.object_version)),
                                                                  extra_inputs=[lambda_build_output])])
                              ]
                              )