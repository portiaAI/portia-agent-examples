import argparse
import uuid

from dotenv import load_dotenv
from helper import check_env_variables, get_cloud_tools, get_local_tools
from portia.config import Config, StorageClass
from portia.execution_context import execution_context
from portia.runner import Runner

EXECUTION_CONTEXT_EMAIL_ADDRESS = "demo@portialabs.ai"
EXECUTION_CONTEXT_USER_NAME = "Nicholas of Patara"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--portia-api-key", required=True)
    parser.add_argument(
        "--query",
        required=True,
    )
    parser.add_argument("--with-execution-context", action="store_true")
    parser.add_argument("--use-cloud-tools", action="store_true")

    args = parser.parse_args()
    load_dotenv()
    check_env_variables()

    my_config = Config.from_default(
        storage_class=StorageClass.CLOUD, portia_api_key=args.portia_api_key
    )

    # Instantiate a Portia runner. Load it with the default config and with the simple tool above.
    tools = get_cloud_tools(my_config) if args.use_cloud_tools else get_local_tools()
    runner = Runner(config=my_config, tools=tools)

    if not args.with_execution_context:
        output = runner.execute_query(args.query)
    else:
        with execution_context(
            end_user_id=str(uuid.uuid4()),
            additional_data={
                "email_address": EXECUTION_CONTEXT_EMAIL_ADDRESS,
                "name": EXECUTION_CONTEXT_USER_NAME,
            },
        ):
            output = runner.execute_query(args.query)
            
    print(f"\"workflow_id\": \"{output.id}\"")
    print(f"Workflow execution is in {output.state}.")
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()