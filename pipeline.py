# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_codepipeline as codepipeline
import aws_cdk.aws_codepipeline_actions as codepipeline_actions
import aws_cdk.core as cdk
import aws_cdk.app_delivery as cicd
import aws_cdk.aws_iam as iam
import aws_cdk.aws_codedeploy as codedeploy
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_secretsmanager as secret
from cdkproj.cdkproj_stack import CdkprojStack



app = cdk.App()
#sv=cdk.SecretValue('a7d0c33591f257579b8aa2854c7c820989b51bec')
#sv=cdk.SecretValue('cac48b8d636457bb7a300e308c5133e0af0d056f')


#sv='a7d0c33591f257579b8aa2854c7c820989b51bec'

# We define a stack that contains the CodePipeline
pipeline_stack = cdk.Stack(app, "PipelineStack")
secret_arn='arn:aws:secretsmanager:us-east-1:417302553802:secret:indrahrpkey-Eg83NU'
sec=secret.Secret.from_secret_arn(pipeline_stack,'secret',secret_arn)
sv=sec.secret_value_from_json("github")



vpc=ec2.Vpc.from_vpc_attributes(pipeline_stack,'vpcatt',availability_zones=['us-east-1a','us-east-1b'],vpc_id=cdk.Fn.import_value('sema4testvpc-VpcID'),
                                private_subnet_ids=[cdk.Fn.import_value('sema4testvpc-PrivateSubnet1ID'),cdk.Fn.import_value('sema4testvpc-PrivateSubnet2ID')],
                                public_subnet_ids=[cdk.Fn.import_value('sema4testvpc-PublicSubnet1ID'),cdk.Fn.import_value('sema4testvpc-PublicSubnet2ID')])


sec_group=ec2.SecurityGroup.from_security_group_id(pipeline_stack,"sec_group","sg-009088aea7d88ad39")

pipeline = codepipeline.Pipeline(pipeline_stack, "CodePipeline",
                                 # Mutating a CodePipeline can cause the currently propagating state to be
                                 # "lost". Ensure we re-run the latest change through the pipeline after it's
                                 # been mutated so we're sure the latest state is fully deployed through.
                                 restart_execution_on_update=True
                                 )

# Configure the CodePipeline source - where your CDK App's source code is hosted
source_output = codepipeline.Artifact()
source = codepipeline_actions.GitHubSourceAction(
    action_name="GitHub",
    output=source_output,
    repo='testrepo',
    oauth_token=sv,
    owner='indrasema4'
)
pipeline.add_stage(
    stage_name="source",
    actions=[source]
)

project = codebuild.PipelineProject(pipeline_stack, "CodeBuild")



synthesized_app = codepipeline.Artifact('codebuild_artifact')
build_action = codepipeline_actions.CodeBuildAction(
    action_name="CodeBuild",
    project=project,
    input=source_output,
    outputs=[synthesized_app]
)
build_stage=pipeline.add_stage(
    stage_name="build",
    actions=[build_action]
)
print ("buildaction type ",type(build_action))

# Optionally, self-update the pipeline stack
self_update_stage = pipeline.add_stage(stage_name="SelfUpdate")
self_update_stage.add_action(cicd.PipelineDeployStackAction(
    stack=pipeline_stack,
    input=synthesized_app,
    admin_permissions=True
))
print (" selfupdate stage",type(self_update_stage))

ecs_deploy_artifact=codepipeline.Artifact('ecs_deploy')
task_def_artifact_path=codepipeline.ArtifactPath(ecs_deploy_artifact,'test')


ecs_deploy_artifact1=codepipeline.Artifact('ecs_deploy1')

ecs_deploy_artifact2=codepipeline.Artifact('ecs_deploy2')

ecs_deploy_artifact3=codepipeline.Artifact('ecs_deploy3')

image_input=codepipeline_actions.CodeDeployEcsContainerImageInput(input=synthesized_app,task_definition_placeholder='IMAGE1_NAME')

#ecs_deploy_artifact.at_path("appspec.yaml")
#ecs_deploy_artifact.at_path("taskdef.json")
#deploy_group='vistatwonodes-deployment-group'
deploy_group='vistabluegreen'
#app_name='vistatwonodes'
app_name='vista2'
#ecs_action=codepipeline_actions.CodeDeployEcsDeployAction(deployment_group=deployment_group,app_spec_template_input='appspec.yaml',task_definition_template_file='taskdef.json',action_name='deploy_bluegreen_ECS')


ecs_app=codedeploy.EcsApplication.from_ecs_application_name(pipeline_stack,"application",app_name)
#ecs_deployment_group=codedeploy.EcsDeploymentConfig.from_ecs_deployment_config_name(pipeline_stack,"deploygroup",deploy_group)
ecs_deployment_group=codedeploy.EcsDeploymentGroup.from_ecs_deployment_group_attributes(pipeline_stack, "deploygroup",application=ecs_app, deployment_group_name=deploy_group)

#act_ecs=codepipeline_actions.CodeDeployEcsDeployAction(variables_namespace='test',deployment_group=ecs_deployment_group,run_order=2,
#                                                       container_image_inputs=[image_input],app_spec_template_input=ecs_deploy_artifact2,
#                                                       task_definition_template_input=ecs_deploy_artifact3,action_name='deploy_bluegreen_ECS')


act_ecs=codepipeline_actions.CodeDeployEcsDeployAction(variables_namespace='test',deployment_group=ecs_deployment_group,
                                                       container_image_inputs=[image_input],app_spec_template_input=synthesized_app,
                                                       task_definition_template_input=synthesized_app,
                                                       action_name='deploy_bluegreen_ECS')

act_ecs.TaskDefinitionTemplateArtifact=synthesized_app
print (str(act_ecs.action_properties))

                                                       #task_definition_template_file=codepipeline.ArtifactPath(synthesized_app,'ss'),task_definition_template_input=synthesized_app,action_name='deploy_bluegreen_ECS')



#print("type is %s",type(ecs_action),str(ecs_action))
###############ecs_cluster=ecs.Cluster.from_cluster_attributes(pipeline_stack,"ecs_cluster",cluster_name="wes-vista2-wesonetestecs58103E9B-OgBZInokvVQg",vpc=vpc,security_groups=[sec_group])
#ecs_to_deploy1=ecs.Ec2Service.from_ec2_service_arn(pipeline_stack, "ecs_service1", "arn:aws:ecs:us-east-1:417302553802:service/wes-vista2-westonetestecsservicevistawebService1D2669D4-ZNH9B2DERB86")
############ecs_to_deploy1=ecs.Ec2Service.from_ec2_service_attributes(pipeline_stack, "ecs_service1",cluster=ecs_cluster , service_arn="arn:aws:ecs:us-east-1:417302553802:service/wes-vista2-westonetestecsservicevistawebService1D2669D4-ZNH9B2DERB86", service_name=None)
###########act_ecs=codepipeline_actions.EcsDeployAction(service=ecs_to_deploy1,action_name='ecs_deploy',run_order=2,image_file=synthesized_app.at_path("dfadfa"))
#ecs_action.bind(pipeline_stack,stage=ecs_stage)





#aws_cdk.aws_codepipeline_actions.CodeDeployEcsDeployAction(*, deployment_group,
#app_spec_template_file=None, app_spec_template_input='', container_image_inputs=None,
#task_definition_template_file=None, task_definition_template_input=None,
#role=None, action_name, run_order=None, variables_namespace=None)
#Bases: aws_cdk.aws_codepipeline_actions

ecs_stage_child=pipeline.node.children[4]
print ('art ',synthesized_app.artifact_name)

print("ecs_stage_chukd ",type(ecs_stage_child))
ecs_stage_child.add_property_override("Name","newname")
ecs_stage_child.add_property_override("Stages.3.Actions.0.Configuration.TaskDefinitionTemplateArtifact",synthesized_app.artifact_name)
print('stages' , str(ecs_stage_child.name))

#stageplacement=codepipeline.StagePlacement(just_after=build_stage)
ecs_stage=pipeline.add_stage(
    actions=[act_ecs],
    #placement=stageplacement,
    stage_name="ECS-Deployment",

)

print ("cons tryp ",type(pipeline))

#print ("child ",str(ecs_stage_child[4]))
#ecs_stage_child.Stages['ECS-Deployment']['Configuration'].TaskDefainitionTemplateArtifact='fadfaaf'


#ecs_action.bind(pipeline_stack,ecs_stage)

print("ecs_stage ",type(ecs_stage))

#ecs_action.bind(pipeline,stage=ecs_stage,bucket=pipeline.artifact_bucket,role=pipeline.role)





# Now add our service stacks
deploy_stage = pipeline.add_stage(stage_name="Deploy")
service_stack_a = CdkprojStack(app, "ServiceStackA")
# Add actions to deploy the stacks in the deploy stage:
deploy_service_aAction = cicd.PipelineDeployStackAction(
    stack=service_stack_a,
    input=synthesized_app,
    # See the note below for details about this option.
    admin_permissions=False
)
deploy_stage.add_action(deploy_service_aAction)

print("type is deployervice action  %s",type(deploy_service_aAction))


#ecs_stage.add_action(deploy_service_aAction)

# Add the necessary permissions for you service deploy action. This role is
# is passed to CloudFormation and needs the permissions necessary to deploy
# stack. Alternatively you can enable [Administrator](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions.html#jf_administrator) permissions above,
# users should understand the privileged nature of this role.
#deploy_service_aAction.add_to_role_policy(iam.PolicyStatement(
#    actions=["*"],
#    resources=["*"]
#))

#service_stack_b = CdkprojStack(app, "ServiceStackB")
#deploy_stage.add_action(cicd.PipelineDeployStackAction(
#    stack=service_stack_b,
#    input=synthesized_app,
#    create_change_set_run_order=998,
#    admin_permissions=True
#))

app.synth()