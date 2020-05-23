#!/usr/bin/env python3

from aws_cdk import core

from pipeline_stack import PipelineStack
from lambda_stack import LambdaStack

app = core.App()

lambda_stack = LambdaStack(app, "LambdaStack")

PipelineStack(app, "PipelineDeployingLambdaStack",
              lambda_code=lambda_stack.lambda_code)

app.synth()
