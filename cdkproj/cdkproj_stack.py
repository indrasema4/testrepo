from aws_cdk import (
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    core
)

class CdkprojStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        #ab=core.Stack(scope,id)
        #print ("ab ", str(ab))
        queue = sqs.Queue(
            self, "CdkprojQueue",
            visibility_timeout=core.Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "CdkprojTopic"
        )

        topic.add_subscription(subs.SqsSubscription(queue))
