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
import os
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
import aws_cdk.aws_lambda_event_sources as lambda_event_sources

class Team3ProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = cognito.UserPool(
            self,
            id = "user-pool-team-3",
            user_pool_name="user-pool-team-3",
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

        user_pool_client = user_pool.add_client(
            "user-pool-client",
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
            "cognito-domain-team-3",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="moviefy"
            )
        )

        admin_group = cognito.CfnUserPoolGroup(
            self,
            id="admin-group",
            user_pool_id=user_pool.user_pool_id,
            group_name="Admin",
            description="Administrators group"
        )

        regular_user_group = cognito.CfnUserPoolGroup(
            self,
            id="regular-user-group",
            user_pool_id=user_pool.user_pool_id,
            group_name="RegularUser",
            description="Regular user group"
        )

        movies_bucket = s3.Bucket(
            self,
            id="movies-team-3",
            bucket_name="movies-team-3"
            )

        movies_table = dynamodb.Table(
            self, "movies-table-team-3",
            table_name="movies-table-team-3",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        genres_table = dynamodb.Table(
            self, "genres-table-team-3",
            table_name="genres-table-team-3",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        actors_table = dynamodb.Table(
            self, "actors-table-team-3",
            table_name="actors-table-team-3",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        directors_table = dynamodb.Table(
            self, "directors-table-team-3",
            table_name="directors-table-team-3",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        feed_table = dynamodb.Table(
            self, "user-table-team-3",
            table_name="user-table-team-3",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        search_table = dynamodb.Table(
            self, "search-table-team-3",
            table_name="search-table-team-3",
            partition_key=dynamodb.Attribute(
                name="movie_id",
                type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        #index by search expression
        search_table.add_global_secondary_index(
            index_name="SearchIndex",
            partition_key=dynamodb.Attribute(
                name="search",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        #index by title
        movies_table.add_global_secondary_index(
            index_name="TitleIndex",
            partition_key=dynamodb.Attribute(
                name="title",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        #index by description
        movies_table.add_global_secondary_index(
            index_name="DescriptionIndex",
            partition_key=dynamodb.Attribute(
                name="description",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        #index by genres
        genres_table.add_global_secondary_index(
            index_name="GenreIndex",
            partition_key=dynamodb.Attribute(
                name="genre",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        genres_table.add_global_secondary_index(
            index_name="MovieIndex",
            partition_key=dynamodb.Attribute(
                name="movie_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        #index by actors
        actors_table.add_global_secondary_index(
            index_name="ActorIndex",
            partition_key=dynamodb.Attribute(
                name="actor",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        actors_table.add_global_secondary_index(
            index_name="MovieIndex",
            partition_key=dynamodb.Attribute(
                name="movie_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        #index by directors
        directors_table.add_global_secondary_index(
            index_name="DirectorIndex",
            partition_key=dynamodb.Attribute(
                name="director",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
        directors_table.add_global_secondary_index(
            index_name="MovieIndex",
            partition_key=dynamodb.Attribute(
                name="movie_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        api = apigateway.RestApi(
            self, "api-gateway-team-3",
            rest_api_name="Team 3",
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=apigateway.Cors.DEFAULT_HEADERS
            )
        )

        # IAM Role for Lambda Functions
        lambda_role = iam.Role(
            self, "lambda-role-team-3",
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

        #authorizer
        admin_authorizer_function = create_lambda_function(
            'admin_authorizer',
            'admin_authorizer.admin_authorizer',
            'admin_authorizer',
            'GET',
            [util_layer],
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'REGION': 'eu-central-1',
                'CLIENT_ID': user_pool_client.user_pool_client_id
            }
        )

        user_authorizer_function = create_lambda_function(
            'user_authorizer',
            'user_authorizer.user_authorizer',
            'user_authorizer',
            'GET',
            [util_layer],
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'REGION': 'eu-central-1',
                'CLIENT_ID': user_pool_client.user_pool_client_id
            }
        )

        both_authorizer_function = create_lambda_function(
            'both_authorizer',
            'both_authorizer.both_authorizer',
            'both_authorizer',
            'GET',
            [util_layer],
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'REGION': 'eu-central-1',
                'CLIENT_ID': user_pool_client.user_pool_client_id
            }
        )

        admin_authorizer = apigateway.RequestAuthorizer(
            self, 'AdminAuthorizer',
            handler=admin_authorizer_function,
            identity_sources=[apigateway.IdentitySource.header('Authorization')],
            results_cache_ttl=Duration.seconds(0)
        )

        user_authorizer = apigateway.RequestAuthorizer(
            self, 'UserAuthorizer',
            handler=user_authorizer_function,
            identity_sources=[apigateway.IdentitySource.header('Authorization')],
            results_cache_ttl=Duration.seconds(0)
        )

        both_authorizer = apigateway.RequestAuthorizer(
            self, 'BothAuthorizer',
            handler=both_authorizer_function,
            identity_sources=[apigateway.IdentitySource.header('Authorization')],
            results_cache_ttl=Duration.seconds(0)
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
                "MOVIES_TABLE": movies_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "SEARCH_TABLE": search_table.table_name
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

        add_subscription_function = create_lambda_function(
            "add_subscription",
            "add_subscription.add_subscription",
            "add_subscription",
            "PUT",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name
            }
        )

        add_subscription_function.add_to_role_policy(iam.PolicyStatement(
            actions=["sns:CreateTopic", "sns:Publish", "sns:Subscribe", "sns:Unsubscribe"],
            resources=["*"],
        ))

        delete_subscription_function = create_lambda_function(
            "delete_subscription",
            "delete_subscription.delete_subscription",
            "delete_subscription",
            "DELETE",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name
            }
        )

        delete_subscription_function.add_to_role_policy(iam.PolicyStatement(
            actions=["sns:CreateTopic",
                     "sns:DeleteTopic",
                     "sns:Publish",
                     "sns:Subscribe",
                     "sns:Unsubscribe",
                     "sns:ListSubscriptionsByTopic"],
            resources=["*"],
        ))

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
                "MOVIES_TABLE": movies_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "SEARCH_TABLE": search_table.table_name,
                "FEED_TABLE": feed_table.table_name
            }
        )

        search_movies_function = create_lambda_function(
            "search_movies",
            "search_movies.search_movies",
            "search_movies",
            "GET",
            [util_layer],
            environment={
                "MOVIES_TABLE": movies_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "SEARCH_TABLE": search_table.table_name
            }
        )

        edit_metadata_function = create_lambda_function(
            "edit_metadata",
            "edit_metadata.edit_metadata",
            "edit_metadata",
            "PUT",
            [util_layer],
            environment={
                "MOVIES_TABLE": movies_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "SEARCH_TABLE": search_table.table_name,
                "SEARCH_TABLE": search_table.table_name
            }
        )

        add_downloaded_genres_function = create_lambda_function(
            "add_downloaded_genres",
            "add_downloaded_genres.add_downloaded_genres",
            "add_downloaded_genres",
            "POST",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name
            }
        )
        
        get_metadata_function = create_lambda_function(
            "get_metadata",
            "get_metadata.get_metadata",
            "get_metadata",
            "GET",
            [util_layer],
            environment={
                "MOVIES_TABLE": movies_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
                "GENRES_TABLE": genres_table.table_name
            }
        )

        get_subscriptions_function = create_lambda_function(
            "get_subscriptions",
            "get_subscriptions.get_subscriptions",
            "get_subscriptions",
            "GET",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name
            }
        )

        notify_subscribed_function = create_lambda_function(
            "notify_subscribers",
            "notify_subscribers.notify_subscribers",
            "notify_subscribers",
            "POST",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name,
                "TABLE_MOVIES": movies_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
                "GENRES_TABLE": genres_table.table_name
            }
        )

        movies_table.grant_stream_read(notify_subscribed_function)

        event_subscription = _lambda.CfnEventSourceMapping(
            scope=self,
            id="companyInsertsOnlyEventSourceMapping",
            function_name=notify_subscribed_function.function_name,
            event_source_arn=movies_table.table_stream_arn,
            maximum_batching_window_in_seconds=1,
            starting_position="LATEST",
            batch_size=1,
        )

        notify_subscribed_function.add_to_role_policy(iam.PolicyStatement(
            actions=["sns:CreateTopic", "sns:Publish", "sns:Subscribe"],
            resources=["*"],
        ))

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

        calculate_rating_function = create_lambda_function(
            "calculate_rating",
            "calculate_rating.calculate_rating",
            "calculate_rating",
            "POST",
            [util_layer]
        )

        calculate_subscription_function = create_lambda_function(
            "calculate_subscription",
            "calculate_subscription.calculate_subscription",
            "calculate_subscription",
            "POST",
            [util_layer]
        )

        calculate_downloads_function = create_lambda_function(
            "calculate_downloads",
            "calculate_downloads.calculate_downloads",
            "calculate_downloads",
            "POST",
            [util_layer]
        )

        add_scores_function = create_lambda_function(
            "add_scores",
            "add_scores.add_scores",
            "add_scores",
            "POST",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name
            }
        )

        # #sqs
        dead_letter_queue = _sqs.Queue(self, "upload-dead-queue-team3", queue_name="upload-dead-queue-team-3")

        upload_queue = _sqs.Queue(
            self, "upload-queue-team-3",
            visibility_timeout=Duration.minutes(5),
            queue_name="upload-queue-team-3",
            dead_letter_queue=_sqs.DeadLetterQueue(max_receive_count=5, queue=dead_letter_queue)
        )

        event_source = lambda_event_sources.SqsEventSource(upload_queue)
        upload_metadata_function.add_event_source(event_source)

        # Step Function Tasks
        upload_movie_task = _sfn_tasks.LambdaInvoke(
            self, "upload-movie-team-3",
            lambda_function=upload_movie_function,
            output_path='$.Payload'
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        send_to_queue_task = _sfn_tasks.SqsSendMessage(
            self, "send-to-queue-team-3",
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

        calculate_rating_task = _sfn_tasks.LambdaInvoke(
            self, "CalculateRating",
            lambda_function=calculate_rating_function,
            output_path="$.Payload"
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        calculate_subscription_task = _sfn_tasks.LambdaInvoke(
            self, "CalculateSubscription",
            lambda_function=calculate_subscription_function,
            output_path="$.Payload"
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        calculate_downloads_task = _sfn_tasks.LambdaInvoke(
            self, "CalculateDownloads",
            lambda_function=calculate_downloads_function,
            output_path="$.Payload"
        ).add_retry(
            interval=Duration.seconds(20),
            max_attempts=5,
            backoff_rate=2
        )

        add_scores_task = _sfn_tasks.LambdaInvoke(
            self, "AddScores",
            lambda_function=add_scores_function,
            output_path="$.Payload"
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

        parallel_state2 = _sfn.Parallel(self, "Parallel State 2")

        parallel_state2.branch(calculate_rating_task)
        parallel_state2.branch(calculate_subscription_task)
        parallel_state2.branch(calculate_downloads_task)

        # Step Function Definition -> chaining tasks
        definition = parallel_state.next(send_to_queue_task)
        definition2 = parallel_state2.next(add_scores_task)
        
        # Step Function
        state_machine = _sfn.StateMachine(
            self, "transcoding-team-3",
            definition=definition,
            comment="Transcoding and uploading new movies",
            timeout=Duration.minutes(5)
        )

        state_machine2 = _sfn.StateMachine(
            self, "adding-new-feed-team-3",
            definition=definition2,
            comment="Adding new movie to feed",
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
        
        add_feed_function = create_lambda_function(
            "add_feed",
            "add_feed.add_feed",
            "add_feed",
            "POST",
            [util_layer],
            environment={
                "STATE_MACHINE_ARN": state_machine2.state_machine_arn,
                "USER_TABLE": feed_table.table_name,
                "MOVIES_TABLE": movies_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
            }
        )

        get_feed_function = create_lambda_function(
            "get_feed",
            "get_feed.get_feed",
            "get_feed",
            "GET",
            [util_layer],
            environment={
                "TABLE_FEED": feed_table.table_name,
                "MOVIES_TABLE": movies_table.table_name
            }
        )

        movie_dynamo_event_source = lambda_event_sources.DynamoEventSource(
            movies_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1
        )
        
        user_dynamo_event_source = lambda_event_sources.DynamoEventSource(
            feed_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1
        )
        
        genres_dynamo_event_source = lambda_event_sources.DynamoEventSource(
            genres_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1
        )

        actors_dynamo_event_source = lambda_event_sources.DynamoEventSource(
            actors_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1
        )

        directors_dynamo_event_source = lambda_event_sources.DynamoEventSource(
            directors_table,
            starting_position=_lambda.StartingPosition.LATEST,
            batch_size=1
        )

        update_feed_function = create_lambda_function(
            "update_feed",
            "update_feed.update_feed",
            "update_feed",
            "POST",
            [util_layer],
            environment={
                "USER_TABLE": feed_table.table_name,
                "MOVIES_TABLE": movies_table.table_name,
                "GENRES_TABLE": genres_table.table_name,
                "ACTORS_TABLE": actors_table.table_name,
                "DIRECTORS_TABLE": directors_table.table_name,
            }
        )


        update_feed_function.add_event_source(user_dynamo_event_source)

        add_feed_function.add_event_source(genres_dynamo_event_source)

        #endpoints
        upload_resource = api.root.add_resource("upload")
        upload_integration = apigateway.LambdaIntegration(upload_function)
        method = upload_resource.add_method("POST", upload_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=admin_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })

        feed_resource = api.root.add_resource("feed")
        get_feed_integration = apigateway.LambdaIntegration(get_feed_function)
        method = feed_resource.add_method("GET", get_feed_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=user_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        upload_user_integration = apigateway.LambdaIntegration(upload_user_function)
        method = feed_resource.add_method("POST", upload_user_integration)
        
        downloaded_resource = feed_resource.add_resource('downloaded')
        add_downloaded_genres_integration = apigateway.LambdaIntegration(add_downloaded_genres_function)
        method = downloaded_resource.add_method("POST", add_downloaded_genres_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=user_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })

        subscriptions_resource = api.root.add_resource("subscriptions")
        add_subscriptions_integration = apigateway.LambdaIntegration(add_subscription_function)
        method = subscriptions_resource.add_method("PUT", add_subscriptions_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=user_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        delete_subscriptions_integration = apigateway.LambdaIntegration(delete_subscription_function)
        method = subscriptions_resource.add_method("DELETE", delete_subscriptions_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=user_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        get_subscriptions_integration = apigateway.LambdaIntegration(get_subscriptions_function)
        method = subscriptions_resource.add_method("GET", get_subscriptions_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=user_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })

        movie_resource = api.root.add_resource("movie")
        get_movie_url_integration = apigateway.LambdaIntegration(get_movie_url_function)
        method = movie_resource.add_method("GET", get_movie_url_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=both_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        delete_resource = movie_resource.add_resource('{id}')
        delete_data_integration = apigateway.LambdaIntegration(delete_data_function)
        method = delete_resource.add_method("DELETE", delete_data_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=admin_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })

        search_resource = api.root.add_resource("search")
        search_movies_integration = apigateway.LambdaIntegration(search_movies_function)
        method = search_resource.add_method("GET", search_movies_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=both_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        
        movie_metadata_resource = api.root.add_resource("metadata")
        movie_metadata_integration = apigateway.LambdaIntegration(get_metadata_function)
        method = movie_metadata_resource.add_method("GET", movie_metadata_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=both_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        edit_metadata_integration = apigateway.LambdaIntegration(edit_metadata_function)
        method = movie_metadata_resource.add_method("PUT", edit_metadata_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=admin_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })

        rating_resource = api.root.add_resource("rating")
        add_rating_integration = apigateway.LambdaIntegration(add_rating_function)
        method = rating_resource.add_method("POST", add_rating_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=user_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        get_rating_integration = apigateway.LambdaIntegration(get_rating_function)
        method = rating_resource.add_method("GET", get_rating_integration, authorization_type=apigateway.AuthorizationType.CUSTOM, authorizer=both_authorizer,
        request_parameters={
            'method.request.header.Authorization': True
        })
        