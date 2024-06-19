import aws_cdk as core
import aws_cdk.assertions as assertions

from project.project_stack import Team3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in project/project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Team3Stack(app, "project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
