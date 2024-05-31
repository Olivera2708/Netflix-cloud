from aws_cdk import (
    aws_s3 as s3, 
    Stack
)
from constructs import Construct

class ProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(
            self, 
            id="movies-team3", 
            bucket_name="movies-team3"
            )
