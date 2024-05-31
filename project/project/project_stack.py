from aws_cdk import (
    aws_s3 as s3, 
    Stack,
    aws_dynamodb as dynamodb
)
from constructs import Construct

class ProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        movies_bucket = s3.Bucket(
            self, 
            id="movies-team3", 
            bucket_name="movies-team3"
            )

        movies_table = dynamodb.Table(
            self, "movies-table-team3",
            table_name="movies-table-team3",
            partition_key=dynamodb.Attribute(
                name="name",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1
        )
