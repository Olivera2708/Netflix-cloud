from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    Stack,
    aws_iam as iam,
    aws_dynamodb as dynamodb, BundlingOptions, Duration,
    aws_apigateway as apigateway,
    aws_stepfunctions as _sfn,
    aws_stepfunctions_tasks as _sfn_tasks,
    aws_sqs as _sqs,
    aws_cognito as cognito
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
import aws_cdk.aws_lambda_event_sources as lambda_event_sources

class Team3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = cognito.UserPool(
            self,
            id = "UserPoolTeam3",
            user_pool_name="UserPoolTeam3",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                username=True,
                email=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            user_verification=cognito.UserVerificationConfig(
                email_subject="Confirm your email address to access our application",
                email_body="""
                Dear User,\n
                Please confirm your email address to gain access to our application. Click {##link##} to verify your account.\n
                Thank you.
                """,
                email_style=cognito.VerificationEmailStyle.LINK
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
                require_symbols=True
            ),
            custom_attributes={
                "first_name": cognito.StringAttribute(mutable=True),
                "last_name": cognito.StringAttribute(mutable=True),
                "birthdate": cognito.StringAttribute(mutable=True),
                "role": cognito.StringAttribute(mutable=True)
            }
        )

        authorizer = apigateway.CognitoUserPoolsAuthorizer(self, "Authorizer",
            cognito_user_pools=[user_pool]
        )


        user_pool_client = user_pool.add_client(
            "UserPoolClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                custom=True,
                user_password=True,
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                scopes=[cognito.OAuthScope.OPENID],
                callback_urls=["http://localhost:4200/search"]
            )
        )

        user_pool.add_domain(
            "CognitoDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="moviefy"
            )
        )

        admin_group = cognito.CfnUserPoolGroup(
            self,
            id="AdminGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="Admin",
            description="Administrators group"
        )

        regular_user_group = cognito.CfnUserPoolGroup(
            self,
            id="RegularUserGroup",
            user_pool_id=user_pool.user_pool_id,
            group_name="RegularUser",
            description="Regular user group"
        )

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

        feed_table = dynamodb.Table(
            self, "user-table-team3",
            table_name="user-table-team3",
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
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=apigateway.Cors.DEFAULT_HEADERS
            )
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

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["cognito-idp:AdminAddUserToGroup"],
                resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool.user_pool_id}"]
            )
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
                memory_size=2048,
                timeout=Duration.minutes(5),
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

        # Define the Lambda Layer
        ffmpeg_layer = _lambda.LayerVersion(
            self, 'FFmpegLayer',
            code=_lambda.AssetCode('lambda_layers/ffmpeg_layer'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description='FFmpeg layer',
        )

        upload_movie_function = create_lambda_function(
            "upload_movie",
            "upload_movie.upload_movie",
            "upload_movie",
            "POST",
            [util_layer],
            environment={
                "BUCKET": movies_bucket.bucket_name
            }
        )

        upload_metadata_function = create_lambda_function(
            "upload_metadata",
            "upload_metadata.upload_metadata",
            "upload_metadata",
            "POST",
            [util_layer],
            environment={
                "BUCKET": movies_bucket.bucket_name,
                "TABLE": movies_table.table_name
            }
        )

        upload_user_function = create_lambda_function(
            "upload_user",
            "upload_user.upload_user",
            "upload_user",
            "POST",
            [util_layer],
            environment={
                "TABLE_MOVIES": movies_table.table_name,
                "TABLE_FEED": feed_table.table_name
            }
        )

        get_rating_function = create_lambda_function(
            "get_rating",
            "get_rating.get_rating",
            "get_rating",
            "GET",
            [util_layer],
            environment={
                "TABLE": movies_table.table_name
            }
        )

        add_rating_function = create_lambda_function(
            "add_rating",
            "add_rating.add_rating",
            "add_rating",
            "POST",
            [util_layer],
            environment={
                "TABLE_MOVIES": movies_table.table_name,
                "TABLE_FEED": feed_table.table_name
            }
        )

        update_user_function = create_lambda_function(
            "edit_user",
            "edit_user.edit_user",
            "edit_user",
            "PUT",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name
            }
        )

        get_movie_url_function = create_lambda_function(
            "get_movie_url",
            "get_movie_url.get_movie_url",
            "get_movie_url",
            "GET",
            [util_layer],
            environment={
                "BUCKET": movies_bucket.bucket_name
            }
        )

        delete_data_function = create_lambda_function(
            "delete_data",
            "delete_data.delete_data",
            "delete_data",
            "DELETE",
            [util_layer],
            environment={
                "BUCKET": movies_bucket.bucket_name,
                "TABLE": movies_table.table_name
            }
        )

        search_movies_function = create_lambda_function(
            "search_movies",
            "search_movies.search_movies",
            "search_movies",
            "POST",
            [util_layer],
            environment={
                "TABLE": movies_table.table_name
            }
        )

        edit_metadata_function = create_lambda_function(
            "edit_metadata",
            "edit_metadata.edit_metadata",
            "edit_metadata",
            "PUT",
            [util_layer],
            environment={
                "TABLE": movies_table.table_name
            }
        )
        
        get_metadata_function = create_lambda_function(
            "get_metadata",
            "get_metadata.get_metadata",
            "get_metadata",
            "GET",
            [util_layer],
            environment={
                "TABLE": movies_table.table_name
            }
        )

        get_subscriptions_function = create_lambda_function(
            "get_subscriptions",
            "get_subscriptions.get_subscriptions",
            "get_subscriptions",
            "GET",
            [util_layer],
            environment={
                "TABLE": feed_table.table_name
            }
        )

        transcode_720p_function = create_lambda_function(
            "transcode_720p_function",
            "transcoding_uploading.transcoding_uploading",
            "transcoding_uploading",
            "POST",
            [util_layer, ffmpeg_layer],
            environment={
                "RESOLUTION": "1280x720",
                "BUCKET": movies_bucket.bucket_name
            }
        )

        transcode_480p_function = create_lambda_function(
            "transcode_480p_function",
            "transcoding_uploading.transcoding_uploading",
            "transcoding_uploading",
            "POST",
            [util_layer, ffmpeg_layer],
            environment={
                "RESOLUTION": "854x480",
                "BUCKET": movies_bucket.bucket_name
            }
        )
     
        transcode_320p_function = create_lambda_function(
            "transcode_320p_function",
            "transcoding_uploading.transcoding_uploading",
            "transcoding_uploading",
            "POST",
            [util_layer, ffmpeg_layer],
            environment={
                "RESOLUTION": "640x360",
                "BUCKET": movies_bucket.bucket_name
            }
        )

        #sqs
        dead_letter_queue = _sqs.Queue(self, "Team3UploadDeadLetterQueue", queue_name="upload-dead-queue-team3")

        upload_queue = _sqs.Queue(
            self, "UploadQueueTeam3",
            visibility_timeout=Duration.minutes(5),
            queue_name="upload-queue-team3",
            dead_letter_queue=_sqs.DeadLetterQueue(max_receive_count=5, queue=dead_letter_queue)
        )

        event_source = lambda_event_sources.SqsEventSource(upload_queue)
        upload_metadata_function.add_event_source(event_source)

        # Step Function Tasks
        upload_movie_task = _sfn_tasks.LambdaInvoke(
            self, "UploadMovie",
            lambda_function=upload_movie_function,
            output_path='$.Payload'
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        send_to_queue_task = _sfn_tasks.SqsSendMessage(
            self, "SendToQueue",
            queue=upload_queue,
            message_body=_sfn.TaskInput.from_json_path_at("$")
        ).add_retry(
            interval=Duration.seconds(5),
            max_attempts=5,
            backoff_rate=2
        )

        transcode_720p_task = _sfn_tasks.LambdaInvoke(
            self, "Transcode720p",
            lambda_function=transcode_720p_function,
            output_path='$.Payload'
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        transcode_480p_task = _sfn_tasks.LambdaInvoke(
            self, "Transcode480p",
            lambda_function=transcode_480p_function,
            output_path='$.Payload'
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        transcode_320p_task = _sfn_tasks.LambdaInvoke(
            self, "Transcode320p",
            lambda_function=transcode_320p_function,
            output_path='$.Payload'
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        #Parallel
        parallel_state = _sfn.Parallel(
            self, "Parallel State"
        )

        parallel_state.branch(upload_movie_task)
        parallel_state.branch(transcode_720p_task)
        parallel_state.branch(transcode_480p_task)
        parallel_state.branch(transcode_320p_task)

        # Step Function Definition -> chaining tasks
        definition = parallel_state.next(send_to_queue_task)
        
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
                "STATE_MACHINE_ARN": state_machine.state_machine_arn,
                "BUCKET": movies_bucket.bucket_name
            }
        )
        
        #endpoints
        upload_resource = api.root.add_resource("upload")
        upload_integration = apigateway.LambdaIntegration(upload_function)
        upload_resource.add_method("POST", upload_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)

        feed_resource = api.root.add_resource("feed")
        upload_user_integration = apigateway.LambdaIntegration(upload_user_function)
        feed_resource.add_method("POST", upload_user_integration)
        edit_user_integration = apigateway.LambdaIntegration(update_user_function)
        feed_resource.add_method("PUT", edit_user_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)

        subscriptions_resource = api.root.add_resource("subscriptions")
        get_subscriptions_integration = apigateway.LambdaIntegration(get_subscriptions_function)
        subscriptions_resource.add_method("GET", get_subscriptions_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)

        movie_resource = api.root.add_resource("movie")
        get_movie_url_integration = apigateway.LambdaIntegration(get_movie_url_function)
        movie_resource.add_method("GET", get_movie_url_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)
        delete_resource = movie_resource.add_resource('{id}')
        delete_data_integration = apigateway.LambdaIntegration(delete_data_function)
        delete_resource.add_method("DELETE", delete_data_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)

        search_resource = api.root.add_resource("search")
        search_movies_integration = apigateway.LambdaIntegration(search_movies_function)
        search_resource.add_method("POST", search_movies_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)
        
        movie_metadata_resource = api.root.add_resource("metadata")
        movie_metadata_integration = apigateway.LambdaIntegration(get_metadata_function)
        movie_metadata_resource.add_method("GET", movie_metadata_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)
        edit_metadata_integration = apigateway.LambdaIntegration(edit_metadata_function)
        movie_metadata_resource.add_method("PUT", edit_metadata_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)

        rating_resource = api.root.add_resource("rating")
        add_rating_integration = apigateway.LambdaIntegration(add_rating_function)
        rating_resource.add_method("POST", add_rating_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)
        get_rating_integration = apigateway.LambdaIntegration(get_rating_function)
        rating_resource.add_method("GET", get_rating_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)
