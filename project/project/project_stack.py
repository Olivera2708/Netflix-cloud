from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    Stack,
    aws_iam as iam,
    aws_dynamodb as dynamodb, BundlingOptions, Duration,
    aws_apigateway as apigateway,
    aws_stepfunctions as _sfn,
    aws_stepfunctions_tasks as _sfn_tasks,
    aws_sqs as _sqs
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
import aws_cdk.aws_lambda_event_sources as lambda_event_sources

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
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AWSStepFunctionsFullAccess")
        )
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")
        )

        def create_lambda_function(id, handler, include_dir, method, layers, environment=None):
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
                environment=environment or {},
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

        #sqs
        upload_queue = _sqs.Queue(
            self, "UploadQueueTeam3",
            visibility_timeout=Duration.seconds(300),
            queue_name="upload-queue-team3"
        )

        event_source = lambda_event_sources.SqsEventSource(upload_queue)
        upload_metadata_function.add_event_source(event_source)

        # Step Function Tasks
        upload_movie_task = _sfn_tasks.LambdaInvoke(
            self, "UploadMovie",
            lambda_function=upload_movie_function,
            output_path='$.Payload'
        )

        send_to_queue_task = _sfn_tasks.SqsSendMessage(
            self, "SendToQueue",
            queue=upload_queue,
            message_body=_sfn.TaskInput.from_json_path_at("$")
        )

        # Step Function Definition -> chaining tasks
        definition = upload_movie_task.next(send_to_queue_task)#.next(upload_metadata_task)
        
        # Step Function
        state_machine = _sfn.StateMachine(
            self, "TranscodingAndUploading",
            definition=definition,
            comment="Transcoding and uploading new movies",
            timeout=Duration.minutes(5)
        )

        upload_function = create_lambda_function(
            "upload",
            "upload.upload",
            "upload",
            "POST",
            [util_layer],
            environment={
                "STATE_MACHINE_ARN": state_machine.state_machine_arn
            }
        )
        
        #endpoints
        resource = api.root.add_resource("upload")
        upload_integration = apigateway.LambdaIntegration(upload_function)
        resource.add_method("POST", upload_integration)

        resource = api.root.add_resource("download")
        download_movie_integration = apigateway.LambdaIntegration(download_movie_function)
        resource.add_method("GET", download_movie_integration)