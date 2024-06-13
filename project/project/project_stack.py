from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    Stack,
    aws_iam as iam,
    aws_dynamodb as dynamodb, BundlingOptions, Duration,
    aws_apigateway as apigateway
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

class Team3Stack(Stack):

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
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1
        )

        #index by title
        movies_table.add_global_secondary_index(
            index_name="TitleIndex",
            partition_key=dynamodb.Attribute(
                name="title",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="year",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
            read_capacity=1,
            write_capacity=1
        )

        #index by genres
        movies_table.add_global_secondary_index(
            index_name="DescriptionIndex",
            partition_key=dynamodb.Attribute(
                name="description",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="title",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL,
            read_capacity=1,
            write_capacity=1
        )

        api = apigateway.RestApi(
            self, "APIGatewayTeam3",
            rest_api_name="API Gateway Team 3",
            description="This is my API Gateway with Lambda integration."
        )

        # IAM Role for Lambda Functions
        lambda_role = iam.Role(
            self, "LambdaRole-team3",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )

        def create_lambda_function(id, handler, include_dir, method, layers):
            function = _lambda.Function(
                self, id,
                runtime=_lambda.Runtime.PYTHON_3_9,
                layers=layers,
                handler=handler,
                code=_lambda.Code.from_asset(include_dir,
                                             bundling=BundlingOptions(
                                                 image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                                                 command=[
                                                     "bash", "-c",
                                                     "pip install --no-cache -r requirements.txt -t /asset-output && cp -r . /asset-output"
                                                 ],
                                             ), ),
                memory_size=128,
                timeout=Duration.seconds(10),
                environment={
                    'TABLE_NAME': movies_table.table_name
                },
                role=lambda_role
            )
            fn_url = function.add_function_url(
                auth_type=_lambda.FunctionUrlAuthType.NONE,
                cors=_lambda.FunctionUrlCorsOptions(
                    allowed_origins=["*"]
                )
            )

            return function

        util_layer = PythonLayerVersion(
            self, 'UtilLambdaLayer',
            entry='libs',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        upload_movie_function = create_lambda_function(
            "upload_movie",
            "upload_movie.upload_movie",
            "upload_movie",
            "POST",
            [util_layer]
        )

        upload_metadata_function = create_lambda_function(
            "upload_metadata",
            "upload_metadata.upload_metadata",
            "upload_metadata",
            "POST",
            [util_layer]
        )

        download_movie_function = create_lambda_function(
            "download_movie",
            "download_movie.download_movie",
            "download_movie",
            "GET",
            [util_layer]
        )

        movies_resource = api.root.add_resource("movies")
        upload_movie_integration = apigateway.LambdaIntegration(upload_movie_function)
        movies_resource.add_method("POST", upload_movie_integration)

        movies_resource = api.root.add_resource("metadata")
        upload_metadata_integration = apigateway.LambdaIntegration(upload_metadata_function)
        movies_resource.add_method("POST", upload_metadata_integration)

        movies_resource = api.root.get_resource("movies")
        download_movie_integration = apigateway.LambdaIntegration(download_movie_function)
        movies_resource.add_method("GET", download_movie_integration)
